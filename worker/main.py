import os
import redis as redis_client
import psycopg2

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/linkops")

def get_db_connection():
    return psycopg2.connect(db_url)

def process_job(link_id: str, conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                link_id VARCHAR(64) NOT NULL,
                timestamp_bucket TIMESTAMP NOT NULL,
                count INTEGER DEFAULT 1,
                last_accessed_at TIMESTAMP NOT NULL,
                PRIMARY KEY (link_id, timestamp_bucket)
            );
        """)
        cur.execute("""
            INSERT INTO analytics (link_id, timestamp_bucket, count, last_accessed_at)
            VALUES (%s, DATE_TRUNC('hour', NOW()), 1, NOW())
            ON CONFLICT (link_id, timestamp_bucket)
            DO UPDATE SET count = analytics.count + 1, last_accessed_at = NOW();
        """, (link_id,))
        conn.commit()

if __name__ == "__main__":
    print("worker: started")
    r = redis_client.from_url(redis_url, decode_responses=True)
    conn = get_db_connection()
    while True:
        job = r.brpop("analytics:queue", timeout=5)
        if job:
            _, link_id = job
            process_job(link_id, conn)

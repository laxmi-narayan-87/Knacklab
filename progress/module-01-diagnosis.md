# Module 01 Diagnosis Notes

## Bug 1: Service Crashes on Startup (Configuration Mismatch)
- Symptom: Importing `app.main` halts during settings initialization with Pydantic `ValidationError`: `DATABASE_URL` field required.
- Hypothesis A: PostgreSQL container is down or not accepting connections on port 5432.
  - Command: `docker compose -f infra/docker-compose.yml ps`
  - Observation: `linkops-postgres` is `Up (healthy)` and bound to port 5432. Hypothesis A disproven.
- Hypothesis B: Environment variable naming mismatch between `.env` and application schema.
  - Command: `Get-Content api\.env`
  - Observation: `.env` defined `DB_URL` while `Settings` model in `api/app/config.py` explicitly declared `DATABASE_URL`. Hypothesis B confirmed.
- Fix: Renamed `DB_URL` to `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/linkops` in `api/.env`.
- Verification proof: `cd api; .\.venv\Scripts\python.exe -c "import app.main; print(app.main.app.title)"` returned `Link Shortener & Analytics API` and `curl -sS http://localhost:3000/health` returned `{"ok":true}`.

## Bug 2: Pagination Boundary Bug & Non-Deterministic Sorting
- Symptom: Users experienced missing items (page 1 skipped records 1-10) and unstable sorting when paginating through links.
- Hypothesis A: The `OFFSET` calculation in `list_links` is off-by-one (`offset = page * limit` instead of `(page - 1) * limit`).
  - Command: `curl.exe -sS "http://localhost:3000/links?page=1&limit=10"`
  - Observation: Returned items starting from offset 10 (`test11` to `test20`), completely skipping items 1-10 on page 1. Hypothesis A confirmed.
- Hypothesis B: The SQL query lacks a deterministic `ORDER BY` clause, causing database rows to shift arbitrarily.
  - Command: Inspected `api/app/routers/links.py` line 62.
  - Observation: `db.query(Link).offset(...).limit(...)` contained no ordering criteria. Hypothesis B confirmed.
- Fix: Updated `offset = (page - 1) * limit` and appended `.order_by(Link.id.asc())` to the SQLAlchemy query.
- Verification proof: Probed Pages 1, 2, and 3 via curl. Page 1 returned `test01`–`test10` (10 items), Page 2 returned `test11`–`test20` (10 items), Page 3 returned `test21`–`test25` (5 items). All 25 items partitioned with zero duplicates and zero omissions.

## Bug 3 (BREAK & FIX): Concurrent Pagination Drift & Deterministic Ordering
- Symptom: Support reported intermittent duplicates across page boundaries under active live traffic where users are creating new short links while others are paginating.
- Underlying Flaw:
  1. Offset pagination (`OFFSET n LIMIT m`) inherently assumes the dataset's relative ordering and offset positions remain immutable across requests.
  2. Without an explicit, unique `ORDER BY` clause, relational databases return rows in arbitrary physical/execution order (non-deterministic). Under concurrent writes or load, internal page reorganizations cause the same row to appear across multiple offsets.
  3. When ordering by descending keys (e.g. newest-first), concurrent inserts at the head of the table shift every existing row to `offset + k`, causing the boundary item of Page 1 to duplicate onto Page 2.
- Fix: Enforced deterministic ordering by appending `.order_by(Link.id.asc())` (or cursor-based pagination for sliding feeds), ensuring all new write operations append strictly outside previously observed offset intervals.
- Concurrent Verification Proof: Executed `api/scripts/test_concurrent_pagination.py` running asynchronous worker inserts during pagination requests. Across Pages 1, 2, and 3, all items partitioned cleanly with exactly 0 duplicates across pages under concurrent traffic.


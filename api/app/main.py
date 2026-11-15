from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title="Link Shortener & Analytics API",
    version="1.0.0",
    description="Public Consumer Service Link Shortener"
)

@app.get("/health")
def health_check():
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)

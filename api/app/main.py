from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers.links import router as links_router
from app.routers.redirect import router as redirect_router

app = FastAPI(
    title="Link Shortener & Analytics API",
    version="1.0.0",
    description="Public Consumer Service Link Shortener"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({
            "detail": exc.errors(),
            "message": "Validation failed: invalid request payload or malformed URL"
        })
    )

@app.get("/health")
def health_check():
    return {"ok": True}

app.include_router(links_router)
app.include_router(redirect_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)

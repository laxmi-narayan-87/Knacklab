import json
import logging
import time
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.config import settings
from app.routers.links import router as links_router
from app.routers.redirect import router as redirect_router

# Configure LinkOps application logger without disrupting Uvicorn's root handler
numeric_level = getattr(logging, settings.log_level.upper(), logging.INFO)
logger = logging.getLogger("linkops")
logger.setLevel(numeric_level)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(numeric_level)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.propagate = False

def emit_structured_log(level: str, msg: str, req_id: str, **kwargs):
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": level.lower(),
        "req_id": req_id,
        "msg": msg,
        **kwargs
    }
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(json.dumps(entry))

app = FastAPI(
    title="Link Shortener & Analytics API",
    version="1.0.0",
    description="Public Consumer Service Link Shortener"
)

@app.middleware("http")
async def structured_request_logging_middleware(request: Request, call_next):
    # Preserve incoming X-Request-ID or generate new correlation ID
    req_id = request.headers.get("x-request-id")
    if not req_id or not req_id.strip():
        req_id = f"req-{uuid.uuid4().hex[:8]}"
    request.state.req_id = req_id

    start_time = time.perf_counter()
    status_code = 500
    path = request.url.path

    # Log request arrival with sanitized metadata
    emit_structured_log("info", "request received", req_id, method=request.method, path=path)

    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = req_id
        return response
    except Exception as exc:
        status_code = 500
        emit_structured_log("error", "unhandled request failure", req_id, error=type(exc).__name__, path=path)
        raise exc
    finally:
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        level = "info" if status_code < 400 else ("warn" if status_code < 500 else "error")
        emit_structured_log(
            level,
            "response sent",
            req_id,
            status=status_code,
            duration_ms=duration_ms,
            path=path
        )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    req_id = getattr(request.state, "req_id", "unknown")
    emit_structured_log("warn", "request validation error", req_id, detail=str(exc.errors())[:200])
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        headers={"X-Request-ID": req_id},
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

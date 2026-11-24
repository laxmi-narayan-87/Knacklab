import json
import hashlib
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Link, ClickEvent

logger = logging.getLogger("linkops.redirect")

def emit_event(level: str, msg: str, req_id: str, **kwargs):
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "level": level.lower(),
        "name": "linkops.redirect",
        "req_id": req_id,
        "msg": msg,
        **kwargs
    }
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(json.dumps(entry))

router = APIRouter(prefix="/r", tags=["redirect"])

@router.get("/{code}")
def redirect_to_long_url(code: str, request: Request, db: Session = Depends(get_db)):
    req_id = getattr(request.state, "req_id", "unknown")
    try:
        link = db.query(Link).filter(Link.code == code).first()
    except Exception as e:
        emit_event("error", "database error during redirect lookup", req_id, code=code, error=str(e))
        # Never leak internal database errors or stack traces to public callers
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    if not link:
        emit_event("warn", "link not found", req_id, code=code)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    if link.expires_at:
        now = datetime.now(timezone.utc)
        expires = link.expires_at.astimezone(timezone.utc) if link.expires_at.tzinfo else link.expires_at.replace(tzinfo=timezone.utc)
        if expires <= now:
            emit_event("warn", "link expired", req_id, code=code, expires_at=expires.isoformat())
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    # Defense-in-depth: verify that destination URL uses an allowed scheme
    from urllib.parse import urlparse
    dest_parsed = urlparse(link.long_url)
    if dest_parsed.scheme.lower() not in ("http", "https"):
        emit_event("warn", "unsafe redirect scheme blocked", req_id, code=code, scheme=dest_parsed.scheme)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    # Record click event asynchronously or safely without blocking redirect
    try:
        client_ip = request.client.host if request.client else "unknown"
        ip_hash = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()
        event = ClickEvent(
            link_id=link.id,
            clicked_at=datetime.now(timezone.utc),
            user_agent=request.headers.get("user-agent", "")[:512],
            referrer=request.headers.get("referer", "")[:512],
            ip_hash=ip_hash
        )
        db.add(event)
        db.commit()
    except Exception as e:
        db.rollback()
        emit_event("warn", "failed to record click event", req_id, link_id=link.id, error=str(e))

    return RedirectResponse(url=link.long_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

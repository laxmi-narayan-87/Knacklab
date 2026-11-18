import hashlib
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Link, ClickEvent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/r", tags=["redirect"])

@router.get("/{code}")
def redirect_to_long_url(code: str, request: Request, db: Session = Depends(get_db)):
    try:
        link = db.query(Link).filter(Link.code == code).first()
    except Exception as e:
        logger.error(f"Database error during redirect lookup for code {code}: {e}")
        # Never leak internal database errors or stack traces to public callers
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    if link.expires_at:
        now = datetime.now(timezone.utc)
        expires = link.expires_at if link.expires_at.tzinfo else link.expires_at.replace(tzinfo=timezone.utc)
        if expires <= now:
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
        logger.warning(f"Failed to record click event for link {link.id}: {e}")

    return RedirectResponse(url=link.long_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

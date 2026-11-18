import secrets
import string
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Link
from app.schemas.link import LinkCreate, LinkResponse

router = APIRouter(prefix="/links", tags=["links"])

ALPHABET = string.ascii_letters + string.digits

def generate_short_code(length: int = 7) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))

def build_short_url(request: Request, code: str) -> str:
    base = str(request.base_url).rstrip("/")
    return f"{base}/r/{code}"

@router.post("", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def create_link(payload: LinkCreate, request: Request, db: Session = Depends(get_db)):
    code = None
    for _ in range(5):
        candidate = generate_short_code(7)
        if not db.query(Link).filter(Link.code == candidate).first():
            code = candidate
            break

    if not code:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate a unique short code. Please try again."
        )

    link = Link(
        code=code,
        long_url=payload.long_url,
        expires_at=payload.expires_at,
        created_by="api_user"
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    return LinkResponse(
        id=link.id,
        code=link.code,
        short_url=build_short_url(request, link.code),
        long_url=link.long_url,
        created_at=link.created_at,
        expires_at=link.expires_at
    )

@router.get("", response_model=List[LinkResponse])
def list_links(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    request: Request = None,
    db: Session = Depends(get_db)
):
    links = db.query(Link).order_by(Link.created_at.desc()).offset(offset).limit(limit).all()
    return [
        LinkResponse(
            id=link.id,
            code=link.code,
            short_url=build_short_url(request, link.code),
            long_url=link.long_url,
            created_at=link.created_at,
            expires_at=link.expires_at
        )
        for link in links
    ]

@router.get("/{id}", response_model=LinkResponse)
def get_link_by_id(id: int, request: Request, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.id == id).first()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found")

    return LinkResponse(
        id=link.id,
        code=link.code,
        short_url=build_short_url(request, link.code),
        long_url=link.long_url,
        created_at=link.created_at,
        expires_at=link.expires_at
    )

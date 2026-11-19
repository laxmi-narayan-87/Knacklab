from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator
from urllib.parse import urlparse

class LinkCreate(BaseModel):
    long_url: str
    expires_at: Optional[datetime] = None
    tags: Optional[List[str]] = None

    @field_validator("long_url", mode="before")
    @classmethod
    def validate_long_url(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("URL must be a string")
        if any(ord(c) < 32 or ord(c) == 127 for c in v):
            raise ValueError("Control characters are not allowed in URL")
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("URL cannot be empty")
        if len(cleaned) > 2048:
            raise ValueError("URL exceeds maximum length of 2048 characters")
        if "\\" in cleaned:
            raise ValueError("Backslashes are not allowed in URL")
        try:
            parsed = urlparse(cleaned)
        except Exception as e:
            raise ValueError(f"Malformed URL: {e}")
        scheme = parsed.scheme.lower()
        if scheme not in ("http", "https"):
            raise ValueError(f"Scheme '{parsed.scheme}' not allowed. Only http and https are permitted.")
        if "@" in parsed.netloc or parsed.username or parsed.password:
            raise ValueError("Userinfo (@) is not allowed in URLs")
        if not parsed.netloc or not parsed.hostname:
            raise ValueError("URL must have a valid hostname and network location")
        return cleaned

    @field_validator("expires_at")
    @classmethod
    def validate_expires_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            now = datetime.now(timezone.utc)
            cmp_v = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
            if cmp_v <= now:
                raise ValueError("expires_at must be in the future")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            if len(v) > 20:
                raise ValueError("Cannot provide more than 20 tags")
            for tag in v:
                if len(tag) > 50:
                    raise ValueError("Tag length cannot exceed 50 characters")
        return v

class LinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    short_url: str
    long_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None

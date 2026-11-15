from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.db import Base

class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(32), unique=True, index=True, nullable=False)
    long_url = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(String(64), index=True, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    clicks = relationship("ClickEvent", back_populates="link", cascade="all, delete-orphan")

class ClickEvent(Base):
    __tablename__ = "click_events"

    id = Column(Integer, primary_key=True, index=True)
    link_id = Column(Integer, ForeignKey("links.id", ondelete="CASCADE"), nullable=False, index=True)
    clicked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    user_agent = Column(String(512), nullable=True)
    referrer = Column(String(512), nullable=True)
    ip_hash = Column(String(64), nullable=True)

    link = relationship("Link", back_populates="clicks")

    __table_args__ = (
        Index("ix_click_events_link_id_clicked_at", "link_id", "clicked_at"),
    )

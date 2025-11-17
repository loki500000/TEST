"""
Saved search SQLAlchemy model
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP,
    ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class SavedSearch(Base):
    """Saved search model"""
    __tablename__ = 'saved_searches'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    search_criteria = Column(JSONB, nullable=False)
    alert_enabled = Column(Boolean, default=True)
    last_checked = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='saved_searches')

    def __repr__(self):
        return f"<SavedSearch(id={self.id}, user_id={self.user_id}, name='{self.name}', alert_enabled={self.alert_enabled})>"

"""
Freelance platform SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class FreelancePlatform(Base):
    """Freelance platform model"""
    __tablename__ = 'freelance_platforms'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    base_url = Column(Text, nullable=False)
    logo_url = Column(Text)
    has_api = Column(Boolean, default=False)
    scraper_enabled = Column(Boolean, default=True)
    last_scraped = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    clients = relationship('Client', back_populates='platform')
    jobs = relationship('Job', back_populates='platform')
    analytics = relationship('PlatformAnalytics', back_populates='platform')

    def __repr__(self):
        return f"<FreelancePlatform(id={self.id}, name='{self.name}', has_api={self.has_api})>"

"""
Company research SQLAlchemy model
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP,
    ForeignKey, CheckConstraint, Text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class CompanyResearch(Base):
    """Company research model"""
    __tablename__ = 'company_research'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, unique=True)
    company_name = Column(String(255))
    linkedin_url = Column(Text)
    linkedin_found = Column(Boolean, default=False)
    linkedin_employee_count = Column(Integer)
    website_url = Column(Text)
    website_found = Column(Boolean, default=False)
    social_media_presence = Column(JSONB)
    recent_news = Column(JSONB)
    digital_footprint_score = Column(Integer)
    research_date = Column(TIMESTAMP, default=datetime.utcnow)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            'digital_footprint_score >= 0 AND digital_footprint_score <= 100',
            name='company_research_digital_footprint_score_check'
        ),
    )

    # Relationships
    client = relationship('Client', back_populates='company_research')

    def __repr__(self):
        return f"<CompanyResearch(id={self.id}, client_id={self.client_id}, company_name='{self.company_name}', score={self.digital_footprint_score})>"

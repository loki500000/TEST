"""
Analytics SQLAlchemy models
"""

from sqlalchemy import (
    Column, Integer, Date, TIMESTAMP,
    ForeignKey, DECIMAL, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class UserAnalytics(Base):
    """User analytics model"""
    __tablename__ = 'user_analytics'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    searches_performed = Column(Integer, default=0)
    jobs_viewed = Column(Integer, default=0)
    jobs_applied = Column(Integer, default=0)
    vetting_reports_generated = Column(Integer, default=0)
    average_trust_score_viewed = Column(DECIMAL(5, 2))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='user_analytics_user_date_key'),
    )

    # Relationships
    user = relationship('User', back_populates='analytics')

    def __repr__(self):
        return f"<UserAnalytics(id={self.id}, user_id={self.user_id}, date={self.date}, searches={self.searches_performed})>"


class PlatformAnalytics(Base):
    """Platform analytics model"""
    __tablename__ = 'platform_analytics'

    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False, index=True)
    platform_id = Column(Integer, ForeignKey('freelance_platforms.id'), index=True)
    jobs_scraped = Column(Integer, default=0)
    new_clients_added = Column(Integer, default=0)
    average_job_budget = Column(DECIMAL(10, 2))
    average_trust_score = Column(DECIMAL(5, 2))
    top_categories = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('date', 'platform_id', name='platform_analytics_date_platform_key'),
    )

    # Relationships
    platform = relationship('FreelancePlatform', back_populates='analytics')

    def __repr__(self):
        return f"<PlatformAnalytics(id={self.id}, platform_id={self.platform_id}, date={self.date}, jobs_scraped={self.jobs_scraped})>"

"""
Client-related SQLAlchemy models
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP, Date,
    ForeignKey, DECIMAL, CheckConstraint, Text, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Client(Base):
    """Client model"""
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    platform_id = Column(Integer, ForeignKey('freelance_platforms.id'), index=True)
    external_client_id = Column(String(255), index=True)
    name = Column(String(255))
    company_name = Column(String(255))
    profile_url = Column(Text)
    location = Column(String(255))
    timezone = Column(String(100))
    member_since = Column(Date)
    total_jobs_posted = Column(Integer, default=0)
    total_hires = Column(Integer, default=0)
    total_spent = Column(DECIMAL(12, 2), default=0)
    payment_verified = Column(Boolean, default=False)
    average_rating = Column(DECIMAL(3, 2))
    response_time_hours = Column(Integer)
    project_completion_rate = Column(DECIMAL(5, 2))
    trust_score = Column(Integer, index=True)
    last_active = Column(TIMESTAMP)
    is_verified = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('platform_id', 'external_client_id', name='clients_platform_external_id_key'),
    )

    # Relationships
    platform = relationship('FreelancePlatform', back_populates='clients')
    reviews = relationship('ClientReview', back_populates='client', cascade='all, delete-orphan')
    red_flags = relationship('ClientRedFlag', back_populates='client', cascade='all, delete-orphan')
    jobs = relationship('Job', back_populates='client')
    company_research = relationship('CompanyResearch', back_populates='client', uselist=False, cascade='all, delete-orphan')
    scam_reports = relationship('ScamReport', back_populates='client')

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', trust_score={self.trust_score})>"


class ClientReview(Base):
    """Client review model"""
    __tablename__ = 'client_reviews'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    reviewer_name = Column(String(255))
    rating = Column(Integer)
    review_text = Column(Text)
    project_title = Column(String(255))
    project_value = Column(DECIMAL(10, 2))
    review_date = Column(Date)
    sentiment_score = Column(DECIMAL(3, 2))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='client_reviews_rating_check'),
    )

    # Relationships
    client = relationship('Client', back_populates='reviews')

    def __repr__(self):
        return f"<ClientReview(id={self.id}, client_id={self.client_id}, rating={self.rating})>"


class ClientRedFlag(Base):
    """Client red flag model"""
    __tablename__ = 'client_red_flags'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    flag_type = Column(String(100), nullable=False)
    description = Column(Text)
    severity = Column(String(50), index=True)
    detected_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_resolved = Column(Boolean, default=False)

    __table_args__ = (
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name='client_red_flags_severity_check'
        ),
    )

    # Relationships
    client = relationship('Client', back_populates='red_flags')

    def __repr__(self):
        return f"<ClientRedFlag(id={self.id}, client_id={self.client_id}, severity='{self.severity}', type='{self.flag_type}')>"

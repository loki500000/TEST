"""
Job-related SQLAlchemy models
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP,
    ForeignKey, DECIMAL, CheckConstraint, Text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Job(Base):
    """Job model"""
    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    platform_id = Column(Integer, ForeignKey('freelance_platforms.id'), index=True)
    external_job_id = Column(String(255))
    title = Column(Text, nullable=False)
    description = Column(Text)
    category = Column(String(255), index=True)
    subcategory = Column(String(255))
    skills_required = Column(ARRAY(Text))
    job_type = Column(String(50))
    budget_min = Column(DECIMAL(10, 2))
    budget_max = Column(DECIMAL(10, 2))
    hourly_rate = Column(DECIMAL(10, 2))
    fixed_price = Column(DECIMAL(10, 2))
    duration = Column(String(100))
    experience_level = Column(String(50))
    client_id = Column(Integer, ForeignKey('clients.id'), index=True)
    posted_date = Column(TIMESTAMP, index=True)
    applications_count = Column(Integer, default=0)
    job_url = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "job_type IN ('hourly', 'fixed', 'both')",
            name='jobs_job_type_check'
        ),
        CheckConstraint(
            "experience_level IN ('entry', 'intermediate', 'expert')",
            name='jobs_experience_level_check'
        ),
        UniqueConstraint('platform_id', 'external_job_id', name='jobs_platform_external_id_key'),
    )

    # Relationships
    platform = relationship('FreelancePlatform', back_populates='jobs')
    client = relationship('Client', back_populates='jobs')
    applications = relationship('JobApplication', back_populates='job', cascade='all, delete-orphan')
    scam_reports = relationship('ScamReport', back_populates='job')

    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title[:50]}', job_type='{self.job_type}', is_active={self.is_active})>"


class JobApplication(Base):
    """Job application model"""
    __tablename__ = 'job_applications'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    applied_at = Column(TIMESTAMP, default=datetime.utcnow)
    status = Column(String(50), default='applied')
    proposal_text = Column(Text)
    bid_amount = Column(DECIMAL(10, 2))
    notes = Column(Text)

    __table_args__ = (
        CheckConstraint(
            "status IN ('applied', 'shortlisted', 'rejected', 'hired')",
            name='job_applications_status_check'
        ),
        UniqueConstraint('user_id', 'job_id', name='job_applications_user_job_key'),
    )

    # Relationships
    user = relationship('User', back_populates='job_applications')
    job = relationship('Job', back_populates='applications')

    def __repr__(self):
        return f"<JobApplication(id={self.id}, user_id={self.user_id}, job_id={self.job_id}, status='{self.status}')>"

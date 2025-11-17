"""
Scam report SQLAlchemy model
"""

from sqlalchemy import (
    Column, Integer, String, TIMESTAMP,
    ForeignKey, CheckConstraint, Text
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class ScamReport(Base):
    """Scam report model"""
    __tablename__ = 'scam_reports'

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('clients.id'), index=True)
    reporter_user_id = Column(Integer, ForeignKey('users.id'))
    job_id = Column(Integer, ForeignKey('jobs.id'))
    report_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    evidence_urls = Column(ARRAY(Text))
    status = Column(String(50), default='pending', index=True)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'dismissed')",
            name='scam_reports_status_check'
        ),
    )

    # Relationships
    client = relationship('Client', back_populates='scam_reports')
    reporter_user = relationship('User', back_populates='scam_reports')
    job = relationship('Job', back_populates='scam_reports')

    def __repr__(self):
        return f"<ScamReport(id={self.id}, client_id={self.client_id}, type='{self.report_type}', status='{self.status}')>"

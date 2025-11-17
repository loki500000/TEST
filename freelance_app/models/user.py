"""
User-related SQLAlchemy models
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, TIMESTAMP,
    ForeignKey, DECIMAL, CheckConstraint, Text
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class User(Base):
    """User model"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    profile_picture_url = Column(Text)
    subscription_tier = Column(
        String(50),
        default='free',
        nullable=False
    )
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)

    __table_args__ = (
        CheckConstraint(
            "subscription_tier IN ('free', 'pro', 'premium')",
            name='users_subscription_tier_check'
        ),
    )

    # Relationships
    skills = relationship('UserSkill', back_populates='user', cascade='all, delete-orphan')
    preferences = relationship('UserPreference', back_populates='user', uselist=False, cascade='all, delete-orphan')
    job_applications = relationship('JobApplication', back_populates='user', cascade='all, delete-orphan')
    scam_reports = relationship('ScamReport', back_populates='reporter_user', cascade='all, delete-orphan')
    saved_searches = relationship('SavedSearch', back_populates='user', cascade='all, delete-orphan')
    analytics = relationship('UserAnalytics', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', subscription_tier='{self.subscription_tier}')>"


class UserSkill(Base):
    """User skills model"""
    __tablename__ = 'user_skills'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    proficiency_level = Column(String(50))
    years_experience = Column(DECIMAL(3, 1))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "proficiency_level IN ('beginner', 'intermediate', 'expert')",
            name='user_skills_proficiency_level_check'
        ),
    )

    # Relationships
    user = relationship('User', back_populates='skills')

    def __repr__(self):
        return f"<UserSkill(id={self.id}, user_id={self.user_id}, skill='{self.skill_name}', level='{self.proficiency_level}')>"


class UserPreference(Base):
    """User preferences model"""
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    preferred_categories = Column(ARRAY(Text))
    min_hourly_rate = Column(DECIMAL(10, 2))
    max_hourly_rate = Column(DECIMAL(10, 2))
    min_fixed_price = Column(DECIMAL(10, 2))
    preferred_job_types = Column(ARRAY(Text))
    preferred_locations = Column(ARRAY(Text))
    email_alerts_enabled = Column(Boolean, default=True)
    alert_frequency = Column(String(50), default='daily')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "alert_frequency IN ('realtime', 'hourly', 'daily', 'weekly')",
            name='user_preferences_alert_frequency_check'
        ),
    )

    # Relationships
    user = relationship('User', back_populates='preferences')

    def __repr__(self):
        return f"<UserPreference(id={self.id}, user_id={self.user_id}, alert_frequency='{self.alert_frequency}')>"

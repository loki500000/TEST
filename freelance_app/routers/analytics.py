"""
Analytics router - User and platform analytics endpoints
"""

from typing import List, Optional
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pydantic import BaseModel, Field

from freelance_app.models.base import get_db
from freelance_app.models.user import User
from freelance_app.models.analytics import UserAnalytics, PlatformAnalytics
from freelance_app.models.job import Job, JobApplication
from freelance_app.models.client import Client
from freelance_app.utils.auth import get_current_user


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


# Response schemas for analytics

class UserAnalyticsResponse(BaseModel):
    """User analytics response"""
    date: date
    searches_performed: int
    jobs_viewed: int
    jobs_applied: int
    vetting_reports_generated: int
    average_trust_score_viewed: Optional[float]

    class Config:
        from_attributes = True


class UserStatsSummary(BaseModel):
    """User statistics summary"""
    total_searches: int = Field(..., description="Total searches performed")
    total_applications: int = Field(..., description="Total job applications")
    total_vetting_reports: int = Field(..., description="Total vetting reports generated")
    applications_by_status: dict = Field(..., description="Application counts by status")
    recent_activity_days: int = Field(..., description="Days since last activity")
    account_age_days: int = Field(..., description="Account age in days")


class PlatformAnalyticsResponse(BaseModel):
    """Platform analytics response"""
    date: date
    platform_id: Optional[int]
    jobs_scraped: int
    new_clients_added: int
    average_job_budget: Optional[float]
    average_trust_score: Optional[float]
    top_categories: Optional[dict]

    class Config:
        from_attributes = True


class PlatformStatsSummary(BaseModel):
    """Platform statistics summary"""
    total_jobs: int = Field(..., description="Total jobs in database")
    total_clients: int = Field(..., description="Total clients in database")
    total_users: int = Field(..., description="Total registered users")
    average_trust_score: float = Field(..., description="Average client trust score")
    jobs_by_category: dict = Field(..., description="Job counts by category")
    recent_jobs_count: int = Field(..., description="Jobs posted in last 7 days")


@router.get(
    "/user",
    response_model=UserStatsSummary,
    summary="Get user analytics summary",
    description="Get analytics summary for the authenticated user"
)
async def get_user_analytics_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics summary for the current user.

    Includes:
    - Total searches performed
    - Total job applications
    - Total vetting reports generated
    - Application status breakdown
    - Account activity metrics

    Requires authentication.
    """
    # Get total searches from analytics
    total_searches = db.query(
        func.sum(UserAnalytics.searches_performed)
    ).filter(
        UserAnalytics.user_id == current_user.id
    ).scalar() or 0

    # Get total applications
    total_applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).count()

    # Get total vetting reports
    total_vetting_reports = db.query(
        func.sum(UserAnalytics.vetting_reports_generated)
    ).filter(
        UserAnalytics.user_id == current_user.id
    ).scalar() or 0

    # Get applications by status
    applications_by_status_query = db.query(
        JobApplication.status,
        func.count(JobApplication.id)
    ).filter(
        JobApplication.user_id == current_user.id
    ).group_by(JobApplication.status).all()

    applications_by_status = {
        status: count for status, count in applications_by_status_query
    }

    # Calculate recent activity
    last_login = current_user.last_login
    if last_login:
        recent_activity_days = (datetime.utcnow() - last_login).days
    else:
        recent_activity_days = -1

    # Calculate account age
    account_age_days = (datetime.utcnow() - current_user.created_at).days

    return {
        "total_searches": int(total_searches),
        "total_applications": total_applications,
        "total_vetting_reports": int(total_vetting_reports),
        "applications_by_status": applications_by_status,
        "recent_activity_days": recent_activity_days,
        "account_age_days": account_age_days
    }


@router.get(
    "/user/daily",
    response_model=List[UserAnalyticsResponse],
    summary="Get daily user analytics",
    description="Get daily analytics breakdown for the authenticated user"
)
async def get_user_daily_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily analytics breakdown for the current user.

    - **days**: Number of days to retrieve (default: 30, max: 365)

    Returns daily analytics including searches, views, applications, and vetting reports.
    """
    # Calculate date range
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    # Get analytics data
    analytics = db.query(UserAnalytics).filter(
        UserAnalytics.user_id == current_user.id,
        UserAnalytics.date >= start_date,
        UserAnalytics.date <= end_date
    ).order_by(desc(UserAnalytics.date)).all()

    return analytics


@router.get(
    "/platform",
    response_model=PlatformStatsSummary,
    summary="Get platform analytics summary",
    description="Get overall platform statistics and analytics"
)
async def get_platform_analytics_summary(
    db: Session = Depends(get_db)
):
    """
    Get comprehensive platform-wide analytics summary.

    Includes:
    - Total jobs, clients, and users
    - Average trust score
    - Job distribution by category
    - Recent activity metrics

    Public endpoint - no authentication required.
    """
    # Get total counts
    total_jobs = db.query(Job).count()
    total_clients = db.query(Client).count()
    total_users = db.query(User).count()

    # Calculate average trust score
    avg_trust_score = db.query(
        func.avg(Client.trust_score)
    ).scalar() or 0.0

    # Get jobs by category
    jobs_by_category_query = db.query(
        Job.category,
        func.count(Job.id)
    ).filter(
        Job.category.isnot(None)
    ).group_by(Job.category).order_by(
        desc(func.count(Job.id))
    ).limit(10).all()

    jobs_by_category = {
        category: count for category, count in jobs_by_category_query
    }

    # Get recent jobs count (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_jobs_count = db.query(Job).filter(
        Job.created_at >= seven_days_ago
    ).count()

    return {
        "total_jobs": total_jobs,
        "total_clients": total_clients,
        "total_users": total_users,
        "average_trust_score": float(avg_trust_score),
        "jobs_by_category": jobs_by_category,
        "recent_jobs_count": recent_jobs_count
    }


@router.get(
    "/platform/daily",
    response_model=List[PlatformAnalyticsResponse],
    summary="Get daily platform analytics",
    description="Get daily analytics breakdown for the platform"
)
async def get_platform_daily_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    platform_id: Optional[int] = Query(None, description="Filter by platform ID"),
    db: Session = Depends(get_db)
):
    """
    Get daily analytics breakdown for the platform.

    - **days**: Number of days to retrieve (default: 30, max: 365)
    - **platform_id**: Filter by specific platform (optional)

    Returns daily analytics including jobs scraped, clients added, and metrics.
    """
    # Calculate date range
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)

    # Build query
    query = db.query(PlatformAnalytics).filter(
        PlatformAnalytics.date >= start_date,
        PlatformAnalytics.date <= end_date
    )

    if platform_id:
        query = query.filter(PlatformAnalytics.platform_id == platform_id)

    analytics = query.order_by(desc(PlatformAnalytics.date)).all()

    return analytics


@router.get(
    "/user/applications",
    response_model=dict,
    summary="Get user application analytics",
    description="Get detailed analytics about user's job applications"
)
async def get_user_application_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics about user's job applications.

    Includes:
    - Total applications
    - Success rate
    - Average bid amount
    - Application timeline
    - Status breakdown

    Requires authentication.
    """
    # Get all applications
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).all()

    if not applications:
        return {
            "total_applications": 0,
            "success_rate": 0.0,
            "average_bid_amount": 0.0,
            "applications_by_status": {},
            "applications_by_month": {}
        }

    # Calculate metrics
    total_applications = len(applications)
    hired_count = len([a for a in applications if a.status == 'hired'])
    success_rate = (hired_count / total_applications * 100) if total_applications > 0 else 0.0

    # Calculate average bid amount
    bid_amounts = [float(a.bid_amount) for a in applications if a.bid_amount]
    average_bid_amount = sum(bid_amounts) / len(bid_amounts) if bid_amounts else 0.0

    # Applications by status
    applications_by_status = {}
    for app in applications:
        status = app.status
        applications_by_status[status] = applications_by_status.get(status, 0) + 1

    # Applications by month
    applications_by_month = {}
    for app in applications:
        month_key = app.applied_at.strftime("%Y-%m")
        applications_by_month[month_key] = applications_by_month.get(month_key, 0) + 1

    return {
        "total_applications": total_applications,
        "success_rate": round(success_rate, 2),
        "hired_count": hired_count,
        "average_bid_amount": round(average_bid_amount, 2),
        "applications_by_status": applications_by_status,
        "applications_by_month": dict(sorted(applications_by_month.items()))
    }


@router.get(
    "/user/vetting-reports",
    response_model=dict,
    summary="Get user vetting report analytics",
    description="Get analytics about user's vetting report usage"
)
async def get_user_vetting_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analytics about user's vetting report usage.

    Includes:
    - Total reports generated
    - Reports by month
    - Average risk scores viewed
    - Subscription tier limits

    Requires authentication.
    """
    # Get total vetting reports from analytics
    total_reports = db.query(
        func.sum(UserAnalytics.vetting_reports_generated)
    ).filter(
        UserAnalytics.user_id == current_user.id
    ).scalar() or 0

    # Get reports by month
    reports_by_month_query = db.query(
        func.to_char(UserAnalytics.date, 'YYYY-MM').label('month'),
        func.sum(UserAnalytics.vetting_reports_generated).label('count')
    ).filter(
        UserAnalytics.user_id == current_user.id
    ).group_by('month').order_by('month').all()

    reports_by_month = {
        month: int(count) for month, count in reports_by_month_query
    }

    # Get average trust score viewed
    avg_trust_score = db.query(
        func.avg(UserAnalytics.average_trust_score_viewed)
    ).filter(
        UserAnalytics.user_id == current_user.id,
        UserAnalytics.average_trust_score_viewed.isnot(None)
    ).scalar() or 0.0

    # Get subscription tier limits
    from freelance_app.config import settings
    tier_limits = {
        'free': settings.FREE_TIER_VETTING_LIMIT,
        'pro': settings.PRO_TIER_VETTING_LIMIT,
        'premium': settings.PREMIUM_TIER_VETTING_LIMIT
    }

    user_limit = tier_limits.get(current_user.subscription_tier, settings.FREE_TIER_VETTING_LIMIT)

    # Get current month's usage
    current_month = datetime.utcnow().strftime("%Y-%m")
    current_month_usage = reports_by_month.get(current_month, 0)

    return {
        "total_reports_generated": int(total_reports),
        "reports_by_month": reports_by_month,
        "average_trust_score_viewed": round(float(avg_trust_score), 2),
        "subscription_tier": current_user.subscription_tier,
        "monthly_limit": user_limit,
        "current_month_usage": current_month_usage,
        "remaining_this_month": max(0, user_limit - current_month_usage) if user_limit != 999999 else "unlimited"
    }

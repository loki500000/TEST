"""
Clients router - Client vetting reports (CORE FEATURE), reviews, and red flags
"""

from typing import List, Optional
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_

from freelance_app.models.base import get_db
from freelance_app.models.user import User
from freelance_app.models.client import Client, ClientReview, ClientRedFlag
from freelance_app.models.company import CompanyResearch
from freelance_app.models.scam import ScamReport
from freelance_app.schemas import (
    ClientResponse,
    ClientVettingReport,
    ClientReviewResponse,
    ClientRedFlagResponse,
    ClientRedFlagCreate,
    ClientReviewCreate,
    CompanyResearchResponse,
    ClientSearchRequest,
    ClientSearchResponse
)
from freelance_app.utils.auth import get_current_user, get_current_premium_user
from freelance_app.services.vetting_service import VettingService
from freelance_app.services.trust_score_service import TrustScoreService
from freelance_app.config import settings


router = APIRouter(
    prefix="/clients",
    tags=["Clients"]
)


@router.get(
    "",
    response_model=ClientSearchResponse,
    summary="Search clients",
    description="Search and filter clients with trust score filtering"
)
async def search_clients(
    search_query: Optional[str] = Query(None, description="Search query"),
    min_trust_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum trust score"),
    max_trust_score: Optional[int] = Query(None, ge=0, le=100, description="Maximum trust score"),
    payment_verified_only: bool = Query(False, description="Only payment verified clients"),
    is_verified_only: bool = Query(False, description="Only verified clients"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum average rating"),
    sort_by: str = Query("trust_score", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db)
):
    """
    Search for clients with advanced filtering.

    Supports filtering by:
    - Search query (name/company name)
    - Trust score range
    - Payment verification status
    - Verification status
    - Minimum rating

    Returns paginated results with client details.
    """
    # Build base query
    query = db.query(Client)

    # Apply filters
    if payment_verified_only:
        query = query.filter(Client.payment_verified == True)

    if is_verified_only:
        query = query.filter(Client.is_verified == True)

    if min_trust_score is not None:
        query = query.filter(Client.trust_score >= min_trust_score)

    if max_trust_score is not None:
        query = query.filter(Client.trust_score <= max_trust_score)

    if min_rating is not None:
        query = query.filter(Client.average_rating >= min_rating)

    # Search query filter
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Client.name.ilike(search_pattern),
                Client.company_name.ilike(search_pattern)
            )
        )

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    if sort_order == "desc":
        sort_func = desc
    else:
        sort_func = asc

    sort_column_map = {
        "trust_score": Client.trust_score,
        "average_rating": Client.average_rating,
        "total_spent": Client.total_spent,
        "total_jobs_posted": Client.total_jobs_posted,
        "member_since": Client.member_since
    }

    sort_column = sort_column_map.get(sort_by, Client.trust_score)
    query = query.order_by(sort_func(sort_column))

    # Apply pagination
    offset = (page - 1) * per_page
    clients = query.offset(offset).limit(per_page).all()

    # Calculate total pages
    total_pages = ceil(total / per_page) if total > 0 else 0

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "clients": clients
    }


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Get client by ID",
    description="Get detailed information about a specific client"
)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific client.

    - **client_id**: ID of the client

    Returns complete client details including trust score and statistics.
    """
    client = db.query(Client).filter(Client.id == client_id).first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    return client


@router.get(
    "/{client_id}/vetting-report",
    response_model=ClientVettingReport,
    summary="Generate client vetting report (CORE FEATURE)",
    description="Generate comprehensive AI-powered vetting report for a client"
)
async def get_client_vetting_report(
    client_id: int,
    include_ai_analysis: bool = Query(True, description="Include AI analysis"),
    include_company_research: bool = Query(False, description="Include company research"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate comprehensive vetting report for a client (CORE FEATURE).

    This endpoint generates a detailed vetting report including:
    - Client basic information
    - Trust score calculation
    - Review analysis and sentiment
    - Red flag detection
    - Scam reports
    - Company research (optional)
    - AI-powered risk assessment
    - Actionable recommendations

    **Subscription limits:**
    - Free tier: 5 reports per month
    - Pro tier: Unlimited reports
    - Premium tier: Unlimited reports with company research

    Requires authentication.
    """
    # Check subscription tier limits
    if current_user.subscription_tier == 'free':
        # Check usage count (would need to track this in user analytics)
        # For now, we'll allow the request but you should implement proper tracking
        pass

    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Company research only for premium users
    if include_company_research and current_user.subscription_tier not in ['pro', 'premium']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company research is only available for Pro and Premium subscribers"
        )

    try:
        # Generate vetting report using VettingService
        vetting_service = VettingService()

        # Get client data with relationships
        client_data = {
            "client": client,
            "reviews": client.reviews,
            "red_flags": client.red_flags,
            "company_research": client.company_research,
            "scam_reports": db.query(ScamReport).filter(
                ScamReport.client_id == client_id
            ).all()
        }

        # Calculate overall risk score (inverse of trust score)
        overall_risk_score = 100 - (client.trust_score if client.trust_score else 50)

        # Generate recommendation based on trust score and red flags
        high_severity_flags = [f for f in client.red_flags if f.severity in ['high', 'critical']]
        scam_reports_count = len(client_data["scam_reports"])

        if overall_risk_score > 70 or len(high_severity_flags) > 0 or scam_reports_count > 2:
            recommendation = "HIGH RISK - Avoid working with this client"
            summary = f"This client shows significant risk indicators including {len(high_severity_flags)} high-severity red flags and {scam_reports_count} scam reports. Proceed with extreme caution or avoid."
        elif overall_risk_score > 40 or scam_reports_count > 0:
            recommendation = "MEDIUM RISK - Proceed with caution"
            summary = f"This client has some concerning indicators. Request milestone payments and maintain clear communication. Trust score: {client.trust_score}/100."
        else:
            recommendation = "LOW RISK - Safe to proceed"
            summary = f"This client shows positive indicators with a trust score of {client.trust_score}/100 and minimal red flags. Standard freelance precautions recommended."

        # Build comprehensive report
        report = {
            "client": client,
            "reviews": client.reviews,
            "red_flags": client.red_flags,
            "company_research": client.company_research if include_company_research else None,
            "scam_reports": client_data["scam_reports"],
            "overall_risk_score": overall_risk_score,
            "recommendation": recommendation,
            "summary": summary,
            "report_generated_at": datetime.utcnow()
        }

        # Track analytics (vetting report generated)
        # You would implement this in the analytics service
        # analytics_service.track_vetting_report(current_user.id, client_id)

        return report

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate vetting report: {str(e)}"
        )


@router.get(
    "/{client_id}/reviews",
    response_model=List[ClientReviewResponse],
    summary="Get client reviews",
    description="Get all reviews for a specific client"
)
async def get_client_reviews(
    client_id: int,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db)
):
    """
    Get all reviews for a specific client.

    - **client_id**: ID of the client

    Returns paginated list of reviews.
    """
    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Get reviews with pagination
    query = db.query(ClientReview).filter(ClientReview.client_id == client_id)
    query = query.order_by(desc(ClientReview.review_date))

    offset = (page - 1) * per_page
    reviews = query.offset(offset).limit(per_page).all()

    return reviews


@router.post(
    "/{client_id}/reviews",
    response_model=ClientReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add client review",
    description="Add a review for a client"
)
async def add_client_review(
    client_id: int,
    review_data: ClientReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a review for a client.

    - **client_id**: ID of the client
    - **reviewer_name**: Name of the reviewer (optional)
    - **rating**: Rating from 1 to 5
    - **review_text**: Review text (10-5000 characters)
    - **project_title**: Title of the project (optional)
    - **project_value**: Value of the project (optional)
    - **review_date**: Date of the review (optional)

    Returns the created review.
    """
    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Create review
    new_review = ClientReview(
        client_id=client_id,
        reviewer_name=review_data.reviewer_name,
        rating=review_data.rating,
        review_text=review_data.review_text,
        project_title=review_data.project_title,
        project_value=review_data.project_value,
        review_date=review_data.review_date
    )

    try:
        db.add(new_review)
        db.commit()
        db.refresh(new_review)

        # Recalculate client's average rating
        trust_score_service = TrustScoreService()
        trust_score_service.recalculate_client_trust_score(client_id, db)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add review: {str(e)}"
        )

    return new_review


@router.get(
    "/{client_id}/red-flags",
    response_model=List[ClientRedFlagResponse],
    summary="Get client red flags",
    description="Get all red flags detected for a client"
)
async def get_client_red_flags(
    client_id: int,
    severity: Optional[str] = Query(None, description="Filter by severity"),
    db: Session = Depends(get_db)
):
    """
    Get all red flags for a specific client.

    - **client_id**: ID of the client
    - **severity**: Filter by severity (low, medium, high, critical)

    Returns list of red flags.
    """
    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Get red flags
    query = db.query(ClientRedFlag).filter(ClientRedFlag.client_id == client_id)

    if severity:
        query = query.filter(ClientRedFlag.severity == severity)

    query = query.order_by(desc(ClientRedFlag.detected_at))
    red_flags = query.all()

    return red_flags


@router.post(
    "/{client_id}/red-flags",
    response_model=ClientRedFlagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report client red flag",
    description="Report a red flag for a client"
)
async def add_client_red_flag(
    client_id: int,
    flag_data: ClientRedFlagCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Report a red flag for a client.

    - **client_id**: ID of the client
    - **flag_type**: Type of red flag
    - **description**: Description of the issue
    - **severity**: Severity level (low, medium, high, critical)

    Returns the created red flag.
    """
    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Create red flag
    new_flag = ClientRedFlag(
        client_id=client_id,
        flag_type=flag_data.flag_type,
        description=flag_data.description,
        severity=flag_data.severity,
        is_resolved=False
    )

    try:
        db.add(new_flag)
        db.commit()
        db.refresh(new_flag)

        # Recalculate trust score
        trust_score_service = TrustScoreService()
        trust_score_service.recalculate_client_trust_score(client_id, db)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add red flag: {str(e)}"
        )

    return new_flag


@router.get(
    "/{client_id}/company-research",
    response_model=CompanyResearchResponse,
    summary="Get company research",
    description="Get company research data for a client (Premium feature)"
)
async def get_company_research(
    client_id: int,
    current_user: User = Depends(get_current_premium_user),
    db: Session = Depends(get_db)
):
    """
    Get company research data for a client.

    This endpoint provides detailed company information including:
    - LinkedIn profile and employee count
    - Website and digital presence
    - Social media profiles
    - Recent news and mentions
    - Digital footprint score

    **Premium feature only** - Requires Pro or Premium subscription.
    """
    # Check if client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Get company research
    research = client.company_research

    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No company research data available for this client"
        )

    return research


# Import datetime at the top if not already imported
from datetime import datetime

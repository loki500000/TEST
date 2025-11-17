"""
Scam Reports router - Community-driven scam reporting and voting
"""

from typing import List, Optional
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_
from pydantic import BaseModel

from freelance_app.models.base import get_db
from freelance_app.models.user import User
from freelance_app.models.scam import ScamReport
from freelance_app.models.client import Client
from freelance_app.models.job import Job
from freelance_app.schemas import ScamReportCreate, ScamReportResponse
from freelance_app.utils.auth import get_current_user


router = APIRouter(
    prefix="/scam-reports",
    tags=["Scam Reports"]
)


class ScamReportSearchResponse(BaseModel):
    """Scam report search response with pagination"""
    total: int
    page: int
    per_page: int
    total_pages: int
    reports: List[ScamReportResponse]


class VoteRequest(BaseModel):
    """Vote request schema"""
    vote_type: str  # "upvote" or "downvote"


@router.get(
    "",
    response_model=ScamReportSearchResponse,
    summary="Search scam reports",
    description="Search and filter scam reports"
)
async def search_scam_reports(
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    job_id: Optional[int] = Query(None, description="Filter by job ID"),
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    status: Optional[str] = Query(None, description="Filter by status (pending, confirmed, dismissed)"),
    min_upvotes: Optional[int] = Query(None, ge=0, description="Minimum upvotes"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db)
):
    """
    Search for scam reports with advanced filtering.

    Supports filtering by:
    - Client ID
    - Job ID
    - Report type
    - Status (pending, confirmed, dismissed)
    - Minimum upvotes

    Returns paginated results with report details.
    """
    # Build base query
    query = db.query(ScamReport)

    # Apply filters
    if client_id is not None:
        query = query.filter(ScamReport.client_id == client_id)

    if job_id is not None:
        query = query.filter(ScamReport.job_id == job_id)

    if report_type:
        query = query.filter(ScamReport.report_type == report_type)

    if status:
        query = query.filter(ScamReport.status == status)

    if min_upvotes is not None:
        query = query.filter(ScamReport.upvotes >= min_upvotes)

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    if sort_order == "desc":
        sort_func = desc
    else:
        sort_func = asc

    sort_column_map = {
        "created_at": ScamReport.created_at,
        "upvotes": ScamReport.upvotes,
        "downvotes": ScamReport.downvotes
    }

    sort_column = sort_column_map.get(sort_by, ScamReport.created_at)
    query = query.order_by(sort_func(sort_column))

    # Apply pagination
    offset = (page - 1) * per_page
    reports = query.offset(offset).limit(per_page).all()

    # Calculate total pages
    total_pages = ceil(total / per_page) if total > 0 else 0

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "reports": reports
    }


@router.get(
    "/{report_id}",
    response_model=ScamReportResponse,
    summary="Get scam report by ID",
    description="Get detailed information about a specific scam report"
)
async def get_scam_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific scam report.

    - **report_id**: ID of the scam report

    Returns complete report details including votes and evidence.
    """
    report = db.query(ScamReport).filter(ScamReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scam report not found"
        )

    return report


@router.post(
    "",
    response_model=ScamReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create scam report",
    description="Submit a new scam report for a client or job"
)
async def create_scam_report(
    report_data: ScamReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a new scam report.

    - **client_id**: ID of the client to report (optional, but either client_id or job_id required)
    - **job_id**: ID of the job to report (optional, but either client_id or job_id required)
    - **report_type**: Type of scam/issue
    - **description**: Detailed description of the issue (10-5000 characters)
    - **evidence_urls**: URLs to evidence (optional)

    Returns the created scam report.

    Requires authentication.
    """
    # Validate that at least one of client_id or job_id is provided
    if not report_data.client_id and not report_data.job_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either client_id or job_id must be provided"
        )

    # Verify client exists if client_id provided
    if report_data.client_id:
        client = db.query(Client).filter(Client.id == report_data.client_id).first()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )

    # Verify job exists if job_id provided
    if report_data.job_id:
        job = db.query(Job).filter(Job.id == report_data.job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )

    # Check if user already reported this client/job
    existing_report = db.query(ScamReport).filter(
        ScamReport.reporter_user_id == current_user.id
    )

    if report_data.client_id:
        existing_report = existing_report.filter(ScamReport.client_id == report_data.client_id)
    if report_data.job_id:
        existing_report = existing_report.filter(ScamReport.job_id == report_data.job_id)

    if existing_report.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reported this client/job"
        )

    # Create scam report
    new_report = ScamReport(
        client_id=report_data.client_id,
        job_id=report_data.job_id,
        reporter_user_id=current_user.id,
        report_type=report_data.report_type,
        description=report_data.description,
        evidence_urls=report_data.evidence_urls,
        status='pending',
        upvotes=0,
        downvotes=0
    )

    try:
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create scam report: {str(e)}"
        )

    return new_report


@router.put(
    "/{report_id}/vote",
    response_model=ScamReportResponse,
    summary="Vote on scam report",
    description="Upvote or downvote a scam report"
)
async def vote_on_scam_report(
    report_id: int,
    vote_request: VoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Vote on a scam report.

    - **report_id**: ID of the report to vote on
    - **vote_type**: Type of vote ("upvote" or "downvote")

    Community voting helps validate and prioritize scam reports.

    Returns the updated scam report with new vote counts.

    Requires authentication.
    """
    # Validate vote type
    if vote_request.vote_type not in ['upvote', 'downvote']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vote type must be 'upvote' or 'downvote'"
        )

    # Get report
    report = db.query(ScamReport).filter(ScamReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scam report not found"
        )

    # Check if user is voting on their own report
    if report.reporter_user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot vote on your own report"
        )

    # Note: In a production app, you'd want to track individual votes
    # to prevent multiple votes from the same user. For now, we'll
    # just increment the counter.

    # Update vote count
    if vote_request.vote_type == 'upvote':
        report.upvotes += 1
    else:
        report.downvotes += 1

    # Auto-confirm reports with high upvote threshold
    if report.upvotes >= 10 and report.status == 'pending':
        report.status = 'confirmed'

    # Auto-dismiss reports with high downvote threshold
    if report.downvotes >= 10 and report.status == 'pending':
        report.status = 'dismissed'

    try:
        db.commit()
        db.refresh(report)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to vote on report: {str(e)}"
        )

    return report


@router.put(
    "/{report_id}/status",
    response_model=ScamReportResponse,
    summary="Update scam report status",
    description="Update the status of a scam report (for moderators)"
)
async def update_scam_report_status(
    report_id: int,
    new_status: str = Query(..., description="New status (pending, confirmed, dismissed)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the status of a scam report.

    - **report_id**: ID of the report
    - **new_status**: New status (pending, confirmed, dismissed)

    This endpoint is typically used by moderators to confirm or dismiss reports.
    Regular users can only update their own reports.

    Returns the updated scam report.

    Requires authentication.
    """
    # Validate status
    if new_status not in ['pending', 'confirmed', 'dismissed']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be 'pending', 'confirmed', or 'dismissed'"
        )

    # Get report
    report = db.query(ScamReport).filter(ScamReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scam report not found"
        )

    # Check if user owns the report (or is admin - you could add admin check here)
    if report.reporter_user_id != current_user.id:
        # In production, check if user is admin/moderator
        # For now, only allow report owner to update
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reports"
        )

    # Update status
    report.status = new_status

    try:
        db.commit()
        db.refresh(report)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update report status: {str(e)}"
        )

    return report


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete scam report",
    description="Delete a scam report (only by report creator)"
)
async def delete_scam_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a scam report.

    - **report_id**: ID of the report to delete

    Only the user who created the report can delete it.

    Returns no content on success.

    Requires authentication.
    """
    # Get report
    report = db.query(ScamReport).filter(ScamReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scam report not found"
        )

    # Check if user owns the report
    if report.reporter_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reports"
        )

    try:
        db.delete(report)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete report: {str(e)}"
        )

    return None


@router.get(
    "/user/me",
    response_model=List[ScamReportResponse],
    summary="Get my scam reports",
    description="Get all scam reports created by the authenticated user"
)
async def get_my_scam_reports(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all scam reports created by the current user.

    Optionally filter by status: pending, confirmed, dismissed.

    Returns paginated list of reports.

    Requires authentication.
    """
    query = db.query(ScamReport).filter(
        ScamReport.reporter_user_id == current_user.id
    )

    if status_filter:
        query = query.filter(ScamReport.status == status_filter)

    # Order by most recent first
    query = query.order_by(desc(ScamReport.created_at))

    # Apply pagination
    offset = (page - 1) * per_page
    reports = query.offset(offset).limit(per_page).all()

    return reports


@router.get(
    "/stats",
    response_model=dict,
    summary="Get scam report statistics",
    description="Get overall statistics about scam reports"
)
async def get_scam_report_stats(
    db: Session = Depends(get_db)
):
    """
    Get overall statistics about scam reports.

    Includes:
    - Total reports
    - Reports by status
    - Most reported clients
    - Most common report types

    Public endpoint - no authentication required.
    """
    # Total reports
    total_reports = db.query(ScamReport).count()

    # Reports by status
    reports_by_status_query = db.query(
        ScamReport.status,
        db.func.count(ScamReport.id)
    ).group_by(ScamReport.status).all()

    reports_by_status = {
        status: count for status, count in reports_by_status_query
    }

    # Most reported clients (top 10)
    most_reported_clients_query = db.query(
        ScamReport.client_id,
        db.func.count(ScamReport.id).label('count')
    ).filter(
        ScamReport.client_id.isnot(None)
    ).group_by(ScamReport.client_id).order_by(
        desc('count')
    ).limit(10).all()

    most_reported_clients = [
        {"client_id": client_id, "report_count": count}
        for client_id, count in most_reported_clients_query
    ]

    # Most common report types
    report_types_query = db.query(
        ScamReport.report_type,
        db.func.count(ScamReport.id).label('count')
    ).group_by(ScamReport.report_type).order_by(
        desc('count')
    ).limit(10).all()

    report_types = {
        report_type: count for report_type, count in report_types_query
    }

    return {
        "total_reports": total_reports,
        "reports_by_status": reports_by_status,
        "most_reported_clients": most_reported_clients,
        "most_common_report_types": report_types
    }

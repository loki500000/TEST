"""
Jobs router - Job search, listings, and application endpoints with AI support
"""

from typing import List, Optional
from math import ceil
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc

from freelance_app.models.base import get_db
from freelance_app.models.user import User
from freelance_app.models.job import Job, JobApplication
from freelance_app.schemas import (
    JobResponse,
    JobSearchRequest,
    JobSearchResponse,
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate
)
from freelance_app.utils.auth import get_current_user
from freelance_app.services.ai_service import AIService


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.get(
    "",
    response_model=JobSearchResponse,
    summary="Search jobs",
    description="Search and filter job listings with AI-powered search support"
)
async def search_jobs(
    search_query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Job category filter"),
    job_type: Optional[str] = Query(None, description="Job type filter (hourly, fixed, both)"),
    experience_level: Optional[str] = Query(None, description="Experience level filter"),
    min_budget: Optional[float] = Query(None, ge=0, description="Minimum budget"),
    max_budget: Optional[float] = Query(None, ge=0, description="Maximum budget"),
    min_hourly_rate: Optional[float] = Query(None, ge=0, description="Minimum hourly rate"),
    max_hourly_rate: Optional[float] = Query(None, ge=0, description="Maximum hourly rate"),
    skills: Optional[List[str]] = Query(None, description="Required skills filter"),
    is_active: bool = Query(True, description="Only active jobs"),
    sort_by: str = Query("posted_date", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db)
):
    """
    Search for jobs with advanced filtering and AI-powered search.

    Supports filtering by:
    - Search query (title/description)
    - Category and subcategory
    - Job type (hourly, fixed, both)
    - Experience level
    - Budget range
    - Hourly rate range
    - Required skills
    - Active status

    Returns paginated results with job details.
    """
    # Build base query
    query = db.query(Job)

    # Apply filters
    if is_active:
        query = query.filter(Job.is_active == True)

    if category:
        query = query.filter(Job.category == category)

    if job_type:
        query = query.filter(Job.job_type == job_type)

    if experience_level:
        query = query.filter(Job.experience_level == experience_level)

    # Budget filters
    if min_budget is not None:
        query = query.filter(
            or_(
                Job.budget_min >= min_budget,
                Job.fixed_price >= min_budget
            )
        )

    if max_budget is not None:
        query = query.filter(
            or_(
                Job.budget_max <= max_budget,
                Job.fixed_price <= max_budget
            )
        )

    # Hourly rate filters
    if min_hourly_rate is not None:
        query = query.filter(Job.hourly_rate >= min_hourly_rate)

    if max_hourly_rate is not None:
        query = query.filter(Job.hourly_rate <= max_hourly_rate)

    # Skills filter - check if any required skill matches
    if skills:
        for skill in skills:
            query = query.filter(Job.skills_required.contains([skill]))

    # Search query filter
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Job.title.ilike(search_pattern),
                Job.description.ilike(search_pattern)
            )
        )

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    if sort_order == "desc":
        sort_func = desc
    else:
        sort_func = asc

    # Map sort_by to actual column
    sort_column_map = {
        "posted_date": Job.posted_date,
        "created_at": Job.created_at,
        "budget_min": Job.budget_min,
        "hourly_rate": Job.hourly_rate,
        "applications_count": Job.applications_count
    }

    sort_column = sort_column_map.get(sort_by, Job.posted_date)
    query = query.order_by(sort_func(sort_column))

    # Apply pagination
    offset = (page - 1) * per_page
    jobs = query.offset(offset).limit(per_page).all()

    # Calculate total pages
    total_pages = ceil(total / per_page) if total > 0 else 0

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
        "jobs": jobs
    }


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job by ID",
    description="Get detailed information about a specific job"
)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific job.

    - **job_id**: ID of the job

    Returns complete job details including client information.
    """
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return job


@router.post(
    "/search/ai",
    response_model=JobSearchResponse,
    summary="AI-powered job search",
    description="Search jobs using natural language with AI assistance"
)
async def ai_search_jobs(
    search_query: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI-powered job search using natural language queries.

    The AI will interpret your search query and find relevant jobs.

    Example queries:
    - "Python developer jobs with at least $50/hour"
    - "Entry-level web development projects under $1000"
    - "React and Node.js freelance opportunities"

    Requires authentication.
    """
    try:
        # Use AI service to process search query
        ai_service = AIService()
        search_params = await ai_service.process_job_search_query(
            query=search_query,
            user_skills=[skill.skill_name for skill in current_user.skills]
        )

        # Build query based on AI interpretation
        query = db.query(Job).filter(Job.is_active == True)

        # Apply AI-suggested filters
        if search_params.get("category"):
            query = query.filter(Job.category == search_params["category"])

        if search_params.get("skills"):
            for skill in search_params["skills"]:
                query = query.filter(Job.skills_required.contains([skill]))

        if search_params.get("min_hourly_rate"):
            query = query.filter(Job.hourly_rate >= search_params["min_hourly_rate"])

        if search_params.get("keywords"):
            search_pattern = f"%{search_params['keywords']}%"
            query = query.filter(
                or_(
                    Job.title.ilike(search_pattern),
                    Job.description.ilike(search_pattern)
                )
            )

        # Get total count
        total = query.count()

        # Apply sorting and pagination
        query = query.order_by(desc(Job.posted_date))
        offset = (page - 1) * per_page
        jobs = query.offset(offset).limit(per_page).all()

        # Calculate total pages
        total_pages = ceil(total / per_page) if total > 0 else 0

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages,
            "jobs": jobs
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI search failed: {str(e)}"
        )


# Job Applications

@router.get(
    "/applications/me",
    response_model=List[JobApplicationResponse],
    summary="Get my job applications",
    description="Get all job applications for the authenticated user"
)
async def get_my_applications(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all job applications for the current user.

    Optionally filter by application status: applied, shortlisted, rejected, hired.

    Returns paginated list of applications.
    """
    query = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    )

    if status_filter:
        query = query.filter(JobApplication.status == status_filter)

    # Order by most recent first
    query = query.order_by(desc(JobApplication.applied_at))

    # Apply pagination
    offset = (page - 1) * per_page
    applications = query.offset(offset).limit(per_page).all()

    return applications


@router.post(
    "/applications",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Apply to a job",
    description="Submit an application for a job posting"
)
async def apply_to_job(
    application_data: JobApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit an application for a job.

    - **job_id**: ID of the job to apply to
    - **proposal_text**: Your application proposal (10-5000 characters)
    - **bid_amount**: Your bid amount (optional)
    - **notes**: Additional notes (optional)

    Returns the created application.
    """
    # Check if job exists
    job = db.query(Job).filter(Job.id == application_data.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check if job is active
    if not job.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot apply to inactive job"
        )

    # Check if user already applied
    existing_application = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.job_id == application_data.job_id
    ).first()

    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this job"
        )

    # Create application
    new_application = JobApplication(
        user_id=current_user.id,
        job_id=application_data.job_id,
        proposal_text=application_data.proposal_text,
        bid_amount=application_data.bid_amount,
        notes=application_data.notes,
        status='applied'
    )

    try:
        db.add(new_application)

        # Increment applications count on job
        job.applications_count += 1

        db.commit()
        db.refresh(new_application)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit application: {str(e)}"
        )

    return new_application


@router.get(
    "/applications/{application_id}",
    response_model=JobApplicationResponse,
    summary="Get application details",
    description="Get details of a specific job application"
)
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific job application.

    - **application_id**: ID of the application

    Only the user who created the application can view it.
    """
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    return application


@router.put(
    "/applications/{application_id}",
    response_model=JobApplicationResponse,
    summary="Update application",
    description="Update a job application"
)
async def update_application(
    application_id: int,
    application_update: JobApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a job application.

    - **application_id**: ID of the application to update
    - **status**: Updated status (optional)
    - **proposal_text**: Updated proposal text (optional)
    - **bid_amount**: Updated bid amount (optional)
    - **notes**: Updated notes (optional)

    Returns the updated application.
    """
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Update fields if provided
    if application_update.status is not None:
        application.status = application_update.status

    if application_update.proposal_text is not None:
        application.proposal_text = application_update.proposal_text

    if application_update.bid_amount is not None:
        application.bid_amount = application_update.bid_amount

    if application_update.notes is not None:
        application.notes = application_update.notes

    try:
        db.commit()
        db.refresh(application)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application: {str(e)}"
        )

    return application


@router.delete(
    "/applications/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Withdraw application",
    description="Withdraw a job application"
)
async def withdraw_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Withdraw a job application.

    - **application_id**: ID of the application to withdraw

    This will permanently delete the application.
    """
    application = db.query(JobApplication).filter(
        JobApplication.id == application_id,
        JobApplication.user_id == current_user.id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    # Get the job to decrement applications count
    job = db.query(Job).filter(Job.id == application.job_id).first()

    try:
        db.delete(application)

        # Decrement applications count
        if job and job.applications_count > 0:
            job.applications_count -= 1

        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to withdraw application: {str(e)}"
        )

    return None

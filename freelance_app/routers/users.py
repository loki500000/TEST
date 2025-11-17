"""
User management router - Profile, skills, and preferences endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from freelance_app.models.base import get_db
from freelance_app.models.user import User, UserSkill, UserPreference
from freelance_app.schemas import (
    UserProfile,
    UserProfileUpdate,
    UserSkillResponse,
    UserSkillCreate,
    UserPreferenceResponse,
    UserPreferenceUpdate
)
from freelance_app.utils.auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user profile",
    description="Get the authenticated user's complete profile"
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's complete profile including skills and preferences.

    Requires authentication.

    Returns user profile with all associated data.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserProfile,
    summary="Update current user profile",
    description="Update the authenticated user's profile information"
)
async def update_my_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.

    - **full_name**: Updated full name (optional)
    - **profile_picture_url**: Updated profile picture URL (optional)
    - **subscription_tier**: Updated subscription tier (optional)

    Returns updated user profile.
    """
    # Update fields if provided
    if profile_update.full_name is not None:
        current_user.full_name = profile_update.full_name

    if profile_update.profile_picture_url is not None:
        current_user.profile_picture_url = profile_update.profile_picture_url

    if profile_update.subscription_tier is not None:
        current_user.subscription_tier = profile_update.subscription_tier

    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )

    return current_user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user account",
    description="Permanently delete the authenticated user's account"
)
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete current user's account.

    WARNING: This action cannot be undone.

    All associated data (skills, preferences, applications, etc.) will be deleted.
    """
    try:
        db.delete(current_user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete account: {str(e)}"
        )

    return None


# Skills endpoints

@router.get(
    "/me/skills",
    response_model=List[UserSkillResponse],
    summary="Get user skills",
    description="Get all skills for the authenticated user"
)
async def get_my_skills(
    current_user: User = Depends(get_current_user)
):
    """
    Get all skills for the current user.

    Returns list of user skills with proficiency levels.
    """
    return current_user.skills


@router.post(
    "/me/skills",
    response_model=UserSkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add user skill",
    description="Add a new skill to the authenticated user's profile"
)
async def add_my_skill(
    skill_data: UserSkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new skill to user's profile.

    - **skill_name**: Name of the skill
    - **proficiency_level**: beginner, intermediate, or expert
    - **years_experience**: Years of experience (optional)

    Returns the created skill.
    """
    # Check if skill already exists for this user
    existing_skill = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id,
        UserSkill.skill_name == skill_data.skill_name
    ).first()

    if existing_skill:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skill '{skill_data.skill_name}' already exists"
        )

    # Create new skill
    new_skill = UserSkill(
        user_id=current_user.id,
        skill_name=skill_data.skill_name,
        proficiency_level=skill_data.proficiency_level,
        years_experience=skill_data.years_experience
    )

    try:
        db.add(new_skill)
        db.commit()
        db.refresh(new_skill)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add skill: {str(e)}"
        )

    return new_skill


@router.put(
    "/me/skills/{skill_id}",
    response_model=UserSkillResponse,
    summary="Update user skill",
    description="Update an existing skill"
)
async def update_my_skill(
    skill_id: int,
    skill_data: UserSkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing skill.

    - **skill_id**: ID of the skill to update
    - **skill_name**: Updated skill name
    - **proficiency_level**: Updated proficiency level
    - **years_experience**: Updated years of experience (optional)

    Returns the updated skill.
    """
    # Get skill
    skill = db.query(UserSkill).filter(
        UserSkill.id == skill_id,
        UserSkill.user_id == current_user.id
    ).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    # Update skill
    skill.skill_name = skill_data.skill_name
    skill.proficiency_level = skill_data.proficiency_level
    skill.years_experience = skill_data.years_experience

    try:
        db.commit()
        db.refresh(skill)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update skill: {str(e)}"
        )

    return skill


@router.delete(
    "/me/skills/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user skill",
    description="Remove a skill from user's profile"
)
async def delete_my_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a skill from user's profile.

    - **skill_id**: ID of the skill to delete

    Returns no content on success.
    """
    # Get skill
    skill = db.query(UserSkill).filter(
        UserSkill.id == skill_id,
        UserSkill.user_id == current_user.id
    ).first()

    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )

    try:
        db.delete(skill)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete skill: {str(e)}"
        )

    return None


# Preferences endpoints

@router.get(
    "/me/preferences",
    response_model=UserPreferenceResponse,
    summary="Get user preferences",
    description="Get job preferences for the authenticated user"
)
async def get_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's job preferences.

    Returns user preferences or creates default if none exist.
    """
    # Get or create preferences
    preferences = current_user.preferences

    if not preferences:
        # Create default preferences
        preferences = UserPreference(user_id=current_user.id)
        try:
            db.add(preferences)
            db.commit()
            db.refresh(preferences)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create preferences: {str(e)}"
            )

    return preferences


@router.put(
    "/me/preferences",
    response_model=UserPreferenceResponse,
    summary="Update user preferences",
    description="Update job preferences for the authenticated user"
)
async def update_my_preferences(
    preferences_update: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's job preferences.

    - **preferred_categories**: List of preferred job categories (optional)
    - **min_hourly_rate**: Minimum acceptable hourly rate (optional)
    - **max_hourly_rate**: Maximum hourly rate (optional)
    - **min_fixed_price**: Minimum fixed price for projects (optional)
    - **preferred_job_types**: List of preferred job types (optional)
    - **preferred_locations**: List of preferred locations (optional)
    - **email_alerts_enabled**: Enable/disable email alerts (optional)
    - **alert_frequency**: Alert frequency: realtime, hourly, daily, weekly (optional)

    Returns updated preferences.
    """
    # Get or create preferences
    preferences = current_user.preferences

    if not preferences:
        preferences = UserPreference(user_id=current_user.id)
        db.add(preferences)

    # Update fields if provided
    if preferences_update.preferred_categories is not None:
        preferences.preferred_categories = preferences_update.preferred_categories

    if preferences_update.min_hourly_rate is not None:
        preferences.min_hourly_rate = preferences_update.min_hourly_rate

    if preferences_update.max_hourly_rate is not None:
        preferences.max_hourly_rate = preferences_update.max_hourly_rate

    if preferences_update.min_fixed_price is not None:
        preferences.min_fixed_price = preferences_update.min_fixed_price

    if preferences_update.preferred_job_types is not None:
        preferences.preferred_job_types = preferences_update.preferred_job_types

    if preferences_update.preferred_locations is not None:
        preferences.preferred_locations = preferences_update.preferred_locations

    if preferences_update.email_alerts_enabled is not None:
        preferences.email_alerts_enabled = preferences_update.email_alerts_enabled

    if preferences_update.alert_frequency is not None:
        preferences.alert_frequency = preferences_update.alert_frequency

    try:
        db.commit()
        db.refresh(preferences)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )

    return preferences


@router.delete(
    "/me/preferences",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reset user preferences",
    description="Reset user preferences to defaults"
)
async def reset_my_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reset user preferences to defaults.

    Deletes existing preferences; defaults will be created on next access.
    """
    if current_user.preferences:
        try:
            db.delete(current_user.preferences)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to reset preferences: {str(e)}"
            )

    return None

"""
Image upload endpoints for Goals and User Profile.
Uses local file storage via the shared storage.py utility.

Endpoints:
  POST   /images/goals/{goal_id}    — upload or replace goal image
  DELETE /images/goals/{goal_id}    — remove goal image
  POST   /images/profile            — upload or replace profile image
  DELETE /images/profile            — remove profile image
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from database import get_db
from JWT_Authentication.auth import get_current_user
from sql_Alchemy_db_model.goals_model import Goals
from sql_Alchemy_db_model.user_models import Users
from routers.storage import upload_image, delete_image, get_image_url

router_images = APIRouter()


# ---------------------------------------------------------------------------
# Goals
# ---------------------------------------------------------------------------

@router_images.post(
    "/goals/{goal_id}",
    summary="Upload or replace a goal image",
    description=(
        "Uploads a JPG, PNG, or WebP image for a specific goal. "
        "If the goal already has an image, the old one is deleted from storage first. "
        "Returns the URL of the uploaded image."
    ),
)
async def upload_goal_image(
    goal_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload or replace the cover image for a goal.

    Args:
        goal_id (int): The ID of the goal to attach the image to.
        file (UploadFile): The image file — JPG, PNG, or WebP, max 2 MB.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        HTTPException: 404 if the goal does not exist or belong to the user.
        HTTPException: 400 for invalid file type or size.
        HTTPException: 500 if file upload fails.

    Returns:
        dict: The goal_id and new image URL.
    """
    goal = (
        db.query(Goals)
        .filter(Goals.id == goal_id, Goals.user_id == current_user["user_id"])
        .first()
    )
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")

    # Delete old image from storage before uploading the new one.
    if goal.image_path:
        delete_image(goal.image_path)

    relative_path = await upload_image(file, folder="goals")
    goal.image_path = relative_path
    db.commit()

    return {
        "goal_id": goal_id,
        "image_url": get_image_url(relative_path)
    }


@router_images.delete(
    "/goals/{goal_id}",
    summary="Remove a goal image",
    description="Deletes the image associated with a goal from local storage and clears the image_path field.",
)
def delete_goal_image(
    goal_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove the cover image from a goal.

    Args:
        goal_id (int): The ID of the goal.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        HTTPException: 404 if the goal does not exist or belong to the user.
        HTTPException: 400 if the goal has no image to delete.

    Returns:
        dict: Confirmation message.
    """
    goal = (
        db.query(Goals)
        .filter(Goals.id == goal_id, Goals.user_id == current_user["user_id"])
        .first()
    )
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    if not goal.image_path:
        raise HTTPException(status_code=400, detail="This goal has no image to delete.")

    delete_image(goal.image_path)
    goal.image_path = None
    db.commit()

    return {"message": f"Image removed from goal {goal_id}."}


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@router_images.post(
    "/profile",
    summary="Upload or replace profile image",
    description=(
        "Uploads a JPG, PNG, or WebP profile photo for the authenticated user. "
        "Replaces the existing photo if one already exists."
    ),
)
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload or replace the authenticated user's profile photo.

    Args:
        file (UploadFile): The image file — JPG, PNG, or WebP, max 2 MB.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        HTTPException: 404 if the user record is not found.
        HTTPException: 400 for invalid file type or size.
        HTTPException: 500 if file upload fails.

    Returns:
        dict: The new image URL.
    """
    user = db.query(Users).filter(Users.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if user.image_path:
        delete_image(user.image_path)

    relative_path = await upload_image(file, folder="profiles")
    user.image_path = relative_path
    db.commit()

    return {"image_url": get_image_url(relative_path)}


@router_images.delete(
    "/profile",
    summary="Remove profile image",
    description="Deletes the authenticated user's profile photo from local storage.",
)
def delete_profile_image(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove the authenticated user's profile photo.

    Args:
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        HTTPException: 404 if the user record is not found.
        HTTPException: 400 if the user has no profile photo to delete.

    Returns:
        dict: Confirmation message.
    """
    user = db.query(Users).filter(Users.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not user.image_path:
        raise HTTPException(status_code=400, detail="No profile image to delete.")

    delete_image(user.image_path)
    user.image_path = None
    db.commit()

    return {"message": "Profile image removed."}
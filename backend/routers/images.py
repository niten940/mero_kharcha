from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from JWT_Authentication.auth import get_current_user
from sql_Alchemy_db_model.goals_model import Goals
from sql_Alchemy_db_model.user_models import Users
from routers.storage import upload_image, delete_image, get_image_url

router_images = APIRouter()

@router_images.post(
    "/goals/{goal_id}",
    summary="Upload or replace a goal image",
)
async def upload_goal_image(
    goal_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = (
        db.query(Goals)
        .filter(Goals.id == goal_id, Goals.user_id == current_user["user_id"])
        .first()
    )
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")

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
)
def delete_goal_image(
    goal_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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


@router_images.post(
    "/profile",
    summary="Upload or replace profile image",
)
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
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
)
def delete_profile_image(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(Users).filter(Users.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not user.image_path:
        raise HTTPException(status_code=400, detail="No profile image to delete.")

    delete_image(user.image_path)
    user.image_path = None
    db.commit()

    return {"message": "Profile image removed."}
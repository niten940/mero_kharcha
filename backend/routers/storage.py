"""
Local file storage utility — handles image uploads to local filesystem.
Used by goals and user profile image endpoints.
"""

import os
import uuid
import shutil
from pathlib import Path
from fastapi import HTTPException, UploadFile
from datetime import datetime

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PROFILE_DIR = os.path.join(UPLOAD_DIR, "profiles")
GOALS_DIR = os.path.join(UPLOAD_DIR, "goals")

# Create directories if they don't exist
os.makedirs(PROFILE_DIR, exist_ok=True)
os.makedirs(GOALS_DIR, exist_ok=True)

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB


async def upload_image(file: UploadFile, folder: str) -> str:
    """
    Upload an image to local storage and return the file path.

    Args:
        file (UploadFile): The uploaded image file.
        folder (str): 'profiles' or 'goals'

    Returns:
        str: The relative path to the uploaded file.

    Raises:
        HTTPException: 400 if file type is not allowed or file exceeds 2 MB.
        HTTPException: 500 if file upload fails.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Use JPG, PNG, or WebP."
        )
    
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File exceeds the 2 MB size limit."
        )
    
    # Generate unique filename
    extension = file.filename.rsplit(".", 1)[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{extension}"
    
    # Determine folder
    if folder == "profiles":
        save_dir = PROFILE_DIR
    elif folder == "goals":
        save_dir = GOALS_DIR
    else:
        save_dir = UPLOAD_DIR
    
    # Save file
    file_path = os.path.join(save_dir, unique_filename)
    try:
        with open(file_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save image: {str(e)}"
        )
    
    # Return the relative path for database storage
    relative_path = f"uploads/{folder}/{unique_filename}"
    return relative_path


def delete_image(image_path: str) -> None:
    """
    Delete an image from local storage.

    Args:
        image_path (str): The relative path to the image file.
    """
    if not image_path:
        return
    
    try:
        # Ensure we're deleting from the correct location
        if image_path.startswith("uploads/"):
            full_path = os.path.join(BASE_DIR, image_path)
        else:
            full_path = os.path.join(BASE_DIR, "uploads", image_path)
        
        if os.path.exists(full_path):
            os.remove(full_path)
    except Exception:
        pass  # Silently fail if file doesn't exist


def get_image_url(image_path: str) -> str:
    """
    Get the full URL for an image.

    Args:
        image_path (str): The relative path to the image.

    Returns:
        str: The full URL to access the image.
    """
    if not image_path:
        return None
    
    # Return the path for the static file serving endpoint
    return f"/static/{image_path}"
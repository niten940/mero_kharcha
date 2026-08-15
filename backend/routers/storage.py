"""
Supabase Storage utility — reusable upload/delete for any entity type.
Handles image uploads to Supabase Storage and returns the public URL.
Used by goals and user profile image endpoints.
"""

import os
import uuid
from fastapi import HTTPException, UploadFile
from supabase import create_client, Client
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB — matches bucket limit


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client using credentials from .env.

    Returns:
        Client: Authenticated Supabase client instance.
    """
    return create_client(SUPABASE_URL, SUPABASE_KEY)


async def upload_image(file: UploadFile, folder: str) -> str:
    """
    Upload an image file to Supabase Storage and return its public URL.

    Validates file type and size before uploading. Generates a UUID-based
    filename to avoid collisions. Folder parameter allows reuse across
    different entity types (e.g. 'goals', 'profiles').

    Args:
        file (UploadFile): The uploaded image file from the request.
        folder (str): Subfolder inside the bucket — e.g. 'goals' or 'profiles'.

    Returns:
        str: Public URL of the uploaded image.

    Raises:
        HTTPException: 400 if file type is not allowed or file exceeds 2 MB.
        HTTPException: 503 if Supabase Storage upload fails.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Use JPG, PNG, or WebP.",
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail="File exceeds the 2 MB size limit.",
        )

    extension = file.filename.rsplit(".", 1)[-1].lower()
    unique_filename = f"{folder}/{uuid.uuid4()}.{extension}"

    try:
        print("DEBUG bucket:", repr(SUPABASE_BUCKET))
        print("DEBUG url:", repr(SUPABASE_URL))
        print("DEBUG key starts with:", repr(SUPABASE_KEY[:10]) if SUPABASE_KEY else "NONE")
        print("DEBUG filename:", repr(unique_filename))


        supabase = get_supabase_client()

        
        # v2.x upload syntax — returns a response object directly
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=unique_filename,
            file=file_bytes,
            file_options={"content-type": file.content_type, "upsert": "false"},
        )



        # Check for errors in the response
        if hasattr(response, "error") and response.error:
            raise HTTPException(
                status_code=503,
                detail=f"Image upload failed: {response.error}",
            )

        # Get public URL
        url_response = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(unique_filename)

        # v2.x returns the URL as a plain string
        if isinstance(url_response, str):
            return url_response
        # Fallback — some versions return an object
        return url_response.public_url

        print("DEBUG upload response type:", type(response))
        print("DEBUG upload response:", response)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Image upload failed: {str(e)}",
        )

def delete_image(image_url: str) -> None:
    """
    Delete an image from Supabase Storage by its public URL.

    Args:
        image_url (str): The full public URL of the image to delete.

    Returns:
        None
    """
    try:
        marker = f"{SUPABASE_BUCKET}/"
        if marker in image_url:
            file_path = image_url.split(marker, 1)[1]
            # Strip query params if any
            file_path = file_path.split("?")[0]
            supabase = get_supabase_client()
            supabase.storage.from_(SUPABASE_BUCKET).remove([file_path])
    except Exception:
        pass
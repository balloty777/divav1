import io
import uuid

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from auth.dependencies import get_current_user
from models.user import User

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)


ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/gif",
}

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PNG, JPEG, WEBP, or GIF image.",
        )

    contents = await file.read()

    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail="Image must be smaller than 5MB.",
        )

    try:
        result = cloudinary.uploader.upload(
            io.BytesIO(contents),
            folder="divav1/avatars",
            public_id=uuid.uuid4().hex,
            resource_type="image",
        )
    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    return {
        "avatar_url": result["secure_url"],
    }
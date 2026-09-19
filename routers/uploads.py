import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from auth.dependencies import get_current_user
from models.user import User

router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)

ALLOWED_CONTENT_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB
AVATAR_DIR = os.path.join("static", "avatars")


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    extension = ALLOWED_CONTENT_TYPES.get(file.content_type)
    if extension is None:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PNG, JPEG, WEBP, or GIF image.",
        )

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Image must be smaller than 5MB.")

    os.makedirs(AVATAR_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extension}"
    with open(os.path.join(AVATAR_DIR, filename), "wb") as out_file:
        out_file.write(contents)

    return {"avatar_url": f"/static/avatars/{filename}"}

from pwdlib import PasswordHash
import jwt
import os
import secrets
import warnings
from dotenv import load_dotenv
from uuid import UUID
from datetime import datetime,timedelta,timezone

load_dotenv()
password_hasher = PasswordHash.recommended()
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    # Secure local-development fallback. Configure JWT_SECRET_KEY in deployment
    # to keep sessions valid across server restarts.
    SECRET_KEY = secrets.token_urlsafe(48)
    warnings.warn(
        "JWT_SECRET_KEY is not set; generated a temporary signing key. "
        "All sessions will expire when the server restarts.",
        RuntimeWarning,
        stacklevel=1,
    )
if len(SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError("JWT_SECRET_KEY must be at least 32 bytes long.")

ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
def hash_password(password: str) -> str:
    return password_hasher.hash(password)
def verify_password(password: str,hashed_password: str,) -> bool:
    return password_hasher.verify(password,hashed_password)
def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id),"exp": expire}
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)

def decode_access_token(token: str) -> UUID:
    payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    user_id = payload.get("sub")
    if user_id is None:
        raise ValueError("Token does not contain a user ID")
    return UUID(user_id)

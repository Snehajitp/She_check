from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone

from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.db.mongodb import get_users_collection

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    users = get_users_collection()
    if await users.find_one({"email": payload.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    doc = {
        "name": payload.name,
        "email": payload.email,
        "hashed_password": hash_password(payload.password),
        "date_of_birth": payload.date_of_birth,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }
    result = await users.insert_one(doc)
    user_id = str(result.inserted_id)
    token = create_access_token({"sub": user_id})
    return TokenResponse(access_token=token, user_id=user_id, name=payload.name)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    users = get_users_collection()
    user = await users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    token = create_access_token({"sub": user_id})
    return TokenResponse(access_token=token, user_id=user_id, name=user["name"])
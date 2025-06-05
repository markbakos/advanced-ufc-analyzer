from fastapi import Request, APIRouter, status, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from server.api.utils.auth import (
    get_hashed_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from server.models.user import UserCreate, UserLogin, User, UserInDB, Token, UserUpdate
from server.core.database import get_database
from datetime import datetime

router = APIRouter()

router.get("/")
async def root(request: Request):
    """Health Check"""
    return {
        "status": "OK",
        "message": "Users API",
        "client_host": request.client.host,
        "client_port": request.client.port
    }

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncIOMotorClient = Depends(get_database)):
    """Register a new user"""

    existing_user = await db["users"].find_one({
        "$or": [
            {"email": user_data.email},
            {"username": user_data.username}
        ]
    })

    if existing_user:
        if existing_user.get("email") == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        if existing_user.get("username") == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    hashed_password = get_hashed_password(user_data.password)

    user_doc = UserInDB(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    result = await db["users"].insert_one(user_doc.model_dump(by_alias=True))

    if result.inserted_id:
        return {
            "message": "User registered successfully",
            "user_id": str(result.inserted_id)
        }

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to create user"
    )

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: AsyncIOMotorClient = Depends(get_database)):
    """Login user and return access and refresh token"""

    user = await db["users"].find_one({"email": user_credentials.email})

    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token({"sub": user["email"]})
    refresh_token = create_refresh_token({"sub": user["email"]})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )
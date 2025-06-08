from bson import ObjectId
from fastapi import Request, APIRouter, status, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
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
from jose import jwt, JWTError
from server.core.config import settings

router = APIRouter()
security = HTTPBearer()

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

async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncIOMotorClient = Depends(get_database)
) -> User:
    """Get current authenticated user"""

    try:
        payload = jwt.decode(
            credentials.credentials,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email = payload.get("sub")
        token_type = payload.get("type")

        if email is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access token"
            )

        user_data = await db["users"].find_one({"email": email})
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        user_data["_id"] = str(user_data["_id"])
        return User(**user_data)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )

@router.get("/current", response_model=User)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Route for using get_current_user function to get the current authenticated user"""
    return current_user

@router.put("/current", response_model=dict)
async def update_user_profile(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncIOMotorClient = Depends(get_database)
):
    """Update selected fields for the current authenticated user"""
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields given to update"
        )

    if "username" in update_data:
        existing_user = await db["users"].find_one({
            "username": update_data["username"],
            "_id": {"$ne": ObjectId(current_user.id)}
        })
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already token"
            )

    if "email" in update_data:
        existing_user = await db["users"].find_one({
            "email": update_data["email"],
            "_id": {"$ne": ObjectId(current_user.id)}
        })
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already token"
            )

    update_data["updated_at"] = datetime.utcnow()

    result = await db["users"].update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": update_data}
    )

    if result.modified_count:
        return {"message": "Profile updated successfully"}

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to update"
    )
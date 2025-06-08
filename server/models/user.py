from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic_core import core_schema
import re
from typing import Optional, Any
from datetime import datetime

# Helper class for MongoDB ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ])
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

class UserBase(BaseModel):
    # Base user model
    username: str = Field(..., min_length=3, max_length=12, description="Username of the user")
    email: str = Field(..., description="Email of the user")

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v):
        if not re.match("^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must be alphanumeric and underscore")
        return v

class UserCreate(UserBase):
    # Data for creating User model
    password: str = Field(..., min_length=8, max_length=32, description="Password of the user")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[a-z]", v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r"[0-9]", v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    # Updateable User data
    username: Optional[str] = Field(None, min_length=3, max_length=12)
    email: Optional[EmailStr] = None

class UserInDB(UserBase):
    # Database model for storing User data
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class User(UserBase):
    # Safe model for User data, no password included
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserLogin(BaseModel):
    # Model used for Login
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")

class Token(BaseModel):
    # Model for Returning Tokens
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None


















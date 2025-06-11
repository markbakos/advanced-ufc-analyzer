import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from jose import jwt
from dns.dnssecalgs import algorithms
from fastapi import HTTPException, status
from bson import ObjectId
import asyncio

from server.api.endpoints.users import get_current_user
from server.models.user import UserCreate, UserLogin, User, UserInDB, Token, UserUpdate
from server.core.config import settings

class TestUserRoutes:
    """Test user routes and endpoints"""

    @pytest.fixture
    def mock_db(self):
        """Mock DB client"""
        db = AsyncMock()
        return db

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI request object"""
        request = MagicMock()
        request.client.host = "127.0.0.1"
        request.client.port = 8000
        return request

    @pytest.fixture
    def sample_user_create(self):
        """Sample user creation data"""
        return UserCreate(
            username="testuser",
            email="test@example.com",
            password="Strongpassword1234"
        )

    @pytest.fixture
    def sample_user_login(self):
        """Sample user login data"""
        return UserLogin(
            email="test@example.com",
            password="Strongpassword1234"
        )

    @pytest.fixture
    def sample_user_db(self):
        """Sample user from database"""
        return {
            "_id": ObjectId(),
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": "$2b$12$hashed_password_here",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    @pytest.fixture
    def sample_user(self):
        """Sample User model instance"""
        return User(
            id=str(ObjectId()),
            username="testuser",
            email="test@example.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    @pytest.fixture
    def valid_token(self):
        """Generate valid JWT token for testing"""
        payload = {
            "sub": "test@example.com",
            "type": "access",
            "exp": datetime.utcnow() + timedelta(minutes=30)
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
        return token

    @pytest.fixture
    def expired_token(self):
        """Generate expired JWT token for testing"""
        payload = {
            "sub": "test@example.com",
            "type": "access",
            "exp": datetime.utcnow() - timedelta(minutes=30)
        }
        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)
        return token

class TestHealthCheck(TestUserRoutes):
    """Test the root health check endpoint"""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, mock_request):
        from server.api.endpoints.users import root

        response = await root(mock_request)

        assert response["status"] == "OK"
        assert response["message"] == "Users API"
        assert response["client_host"] == "127.0.0.1"
        assert response["client_port"] == 8000

class TestUserRegistration(TestUserRoutes):
    """Test user registration"""

    @pytest.mark.asyncio
    async def test_registration_success(self, mock_db, sample_user_create):
        """Returns all success"""
        from server.api.endpoints.users import register_user

        mock_db["users"].find_one = AsyncMock(return_value=None)
        mock_db["users"].insert_one = AsyncMock(return_value=MagicMock(inserted_id=ObjectId()))

        with patch('server.api.endpoints.users.get_hashed_password') as mock_hash:
            mock_hash.return_value = "hashed_password"

            response = await register_user(sample_user_create, mock_db)

        assert response["message"] == "User registered successfully"
        assert "user_id" in response

    @pytest.mark.asyncio
    async def test_registration_email_taken(self, mock_db, sample_user_create, sample_user_db):
        """Try with taken email"""
        from server.api.endpoints.users import register_user

        # mock user with same email
        mock_db["users"].find_one = AsyncMock(return_value=sample_user_db)

        with pytest.raises(HTTPException) as exc_info:
            await register_user(sample_user_create, mock_db)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_registration_username_taken(self, mock_db, sample_user_create):
        """Try with taken username"""
        from server.api.endpoints.users import register_user

        # mock user with same username
        existing_user = {"username": "testuser", "email": "different@example.com"}
        mock_db["users"].find_one = AsyncMock(return_value=existing_user)

        with pytest.raises(HTTPException) as exc_info:
            await register_user(sample_user_create, mock_db)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already taken" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_registration_database_error(self, mock_db, sample_user_create):
        """Test with database insertion failure"""
        from server.api.endpoints.users import register_user

        mock_db["users"].find_one = AsyncMock(return_value=None)
        mock_db["users"].insert_one = AsyncMock(return_value=MagicMock(inserted_id=None))

        with patch('server.api.endpoints.users.get_hashed_password') as mock_hash:
            mock_hash.return_value = "hashed_password"

            with pytest.raises(HTTPException) as exc_info:
                await register_user(sample_user_create, mock_db)

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to create user" in str(exc_info.value.detail)

class TestUserLogin(TestUserRoutes):
    """Test user login functionality"""

    @pytest.mark.asyncio
    async def test_login_success(self, mock_db, sample_user_login, sample_user_db):
        """Test successful user login"""
        from server.api.endpoints.users import login_user

        mock_db["users"].find_one = AsyncMock(return_value=sample_user_db)

        with patch('server.api.endpoints.users.verify_password') as mock_verify, \
             patch('server.api.endpoints.users.create_access_token') as mock_access, \
             patch('server.api.endpoints.users.create_refresh_token') as mock_refresh:

            mock_verify.return_value = True
            mock_access.return_value = "access_token_here"
            mock_refresh.return_value = "refresh_token_here"

            response = await login_user(sample_user_login, mock_db)

            assert isinstance(response, Token)
            assert response.access_token == "access_token_here"
            assert response.refresh_token == "refresh_token_here"
            mock_db["users"].find_one.assert_called_once_with({"email": sample_user_login.email})

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, mock_db, sample_user_login, sample_user_db):
        """Test user login with non-existent user"""
        from server.api.endpoints.users import login_user

        mock_db["users"].find_one = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await login_user(sample_user_login, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, mock_db, sample_user_login, sample_user_db):
        """Test user login with incorrect password"""
        from server.api.endpoints.users import login_user

        mock_db["users"].find_one = AsyncMock(return_value=sample_user_db)

        with patch('server.api.endpoints.users.verify_password') as mock_verify:
            mock_verify.return_value = False

            with pytest.raises(HTTPException) as exc_info:
                await login_user(sample_user_login, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in str(exc_info.value.detail)

class TestAuthentication(TestUserLogin):
    """Test authentication middleware and functions"""

    @pytest.mark.asyncio
    async def test_get_current_user_success(self, mock_db, sample_user_db, valid_token):
        """Test successful user authentication"""
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)
        mock_db["users"].find_one = AsyncMock(return_value=sample_user_db)

        user = await get_current_user(credentials, mock_db)

        assert isinstance(user, User)
        assert user.email == sample_user_db["email"]
        assert user.username == sample_user_db["username"]

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, mock_db, sample_user_db, valid_token):
        """Test invalid token user authentication"""
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_token")

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials, mock_db)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid access token" in str(exc_info.value.detail)


if __name__ == '__main__':
    pytest.main([__file__, "-v", "--tb=short"])
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from bson import ObjectId
import asyncio

from server.models.user import UserCreate, UserLogin, User

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

    @pytest.fixture
    def expired_token(self):
        """Generate expired JWT token for testing"""
        payload = {
            "sub": "test@example.com",
            "type": "access",
            "exp": datetime.utcnow() - timedelta(minutes=30)
        }

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

if __name__ == '__main__':
    pytest.main([__file__, "-v", "--tb=short"])
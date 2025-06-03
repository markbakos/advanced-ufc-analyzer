from fastapi import APIRouter
from server.api.endpoints import predict, users

router = APIRouter()

router.include_router(predict.router, prefix="/predict", tags=["predict"])
router.include_router(users.router, prefix="/users", tags=["users"])
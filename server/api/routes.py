from fastapi import APIRouter
from server.api.endpoints import predict

router = APIRouter()

router.include_router(predict.router, prefix="/predict", tags=["predict"])
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from server.api.routes import router as api_router
from server.core.config import settings
from server.core.database import connect_to_mongo, close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await connect_to_mongo()
    yield
    #shutdown
    await close_mongo_connection()

def get_application() -> FastAPI:
    """Create and config FastAPI application"""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    return application

app = get_application()
app.include_router(api_router, prefix=settings.API_PREFIX)
@app.get('/')
async def root():
    """Health check"""
    return {"status": "OK", "message": "API is running"}

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
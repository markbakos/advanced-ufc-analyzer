from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.core.config import settings

def get_application() -> FastAPI:
    """Create and config FastAPI application"""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
    )

    application.add_middleware(
        CORSMiddleware,
        allowed_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    @application.get('/')
    async def root():
        """Health check"""
        return {"status": "OK", "message": "API is running"}

    return application

app = get_application()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from pathlib import Path

from app.config import settings
from app.presentation.routes import users, tests, questions, attempts, results, exam_types, subjects

def create_application() -> FastAPI:
    # Initialize FastAPI app with root path for reverse proxy
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        root_path=settings.ROOT_PATH,
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add GZip compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Include API routes
    app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
    app.include_router(attempts.router, prefix=f"{settings.API_V1_STR}/attempts", tags=["attempts"])
    # app.include_router(categories.router, prefix=f"{settings.API_V1_STR}/categories", tags=["categories"])
    app.include_router(exam_types.router, prefix=f"{settings.API_V1_STR}/exam-types", tags=["exam-types"])
    app.include_router(questions.router, prefix=f"{settings.API_V1_STR}/questions", tags=["questions"])
    app.include_router(results.router, prefix=f"{settings.API_V1_STR}/results", tags=["results"])
    app.include_router(subjects.router, prefix=f"{settings.API_V1_STR}/subjects", tags=["subjects"])
    app.include_router(tests.router, prefix=f"{settings.API_V1_STR}/tests", tags=["tests"])

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app

app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        reload=settings.DEBUG,
        proxy_headers=True,
        forwarded_allow_ips="*"
    )

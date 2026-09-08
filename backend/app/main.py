"""
Team Task Manager – FastAPI application factory.
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import inspect, text
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.migrations import ensure_user_organization_column
from app.db.session import Base, engine
 
# Static files are copied to /app/static inside the container
STATIC_DIR = Path("/app/static")
 
 
def ensure_user_organization_column(engine):
    """Lightweight migration for deployments that already have a users table."""
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "organization_name" not in columns:
        with engine.begin() as connection:
            connection.execute(text(
                "ALTER TABLE users ADD COLUMN organization_name VARCHAR(128) DEFAULT '' NOT NULL"
            ))


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_user_organization_column(engine)
    yield
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "Full-stack Team Task Manager API. "
            "Role-based access control, project management, and task tracking."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
 
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
 
    # API routes first — these take priority over catch-all
    app.include_router(api_router)
 
    # Health check
    @app.get("/health", tags=["Health"])
    def health():
        return {"status": "ok", "version": settings.APP_VERSION}
 
    # Serve React static assets
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
 
    # Catch-all: serve index.html for every other route (React Router handles it)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        index = STATIC_DIR / "index.html"
        if index.exists():
            return FileResponse(str(index))
        return {"detail": "Frontend not found"}
 
    return app
 
 
app = create_app()

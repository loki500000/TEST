"""
API Routers package - Export all routers for the freelance app
"""

from freelance_app.routers.auth import router as auth_router
from freelance_app.routers.users import router as users_router
from freelance_app.routers.jobs import router as jobs_router
from freelance_app.routers.clients import router as clients_router
from freelance_app.routers.analytics import router as analytics_router
from freelance_app.routers.scam_reports import router as scam_reports_router


__all__ = [
    "auth_router",
    "users_router",
    "jobs_router",
    "clients_router",
    "analytics_router",
    "scam_reports_router",
]


# Optional: Function to register all routers with a FastAPI app
def register_routers(app):
    """
    Register all routers with a FastAPI application instance

    Usage:
        from fastapi import FastAPI
        from freelance_app.routers import register_routers

        app = FastAPI()
        register_routers(app)

    Args:
        app: FastAPI application instance
    """
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(jobs_router)
    app.include_router(clients_router)
    app.include_router(analytics_router)
    app.include_router(scam_reports_router)

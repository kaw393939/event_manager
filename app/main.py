from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse
from app.database import Database
from app.dependencies import get_settings
from app.routers import user_routes
from app.utils.api_description import getDescription
from sqlalchemy.exc import SQLAlchemyError

app = FastAPI(
    title="User Management",
    description=getDescription(),
    version="0.0.1",
    contact={
        "name": "API Support",
        "url": "http://www.example.com/support",
        "email": "support@example.com",
    },
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

@app.on_event("startup")
async def startup_event():
    """
    Startup event where the database is initialized.
    """
    settings = get_settings()
    try:
        # Initialize the database connection
        Database.initialize(settings.database_url, settings.debug)
        # Any other necessary startup logic, like creating tables or migrations
    except SQLAlchemyError as e:
        # Handle database connection issues here, and log them if necessary
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to the database")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event where we close the database connection gracefully.
    """
    Database.close()

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """
    Global exception handler for any uncaught exceptions in the app.
    """
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )

# Handle HTTP-specific exceptions as well
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """
    Handle specific HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Include user routes
app.include_router(user_routes.router)

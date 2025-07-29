from builtins import Exception
from fastapi import FastAPI
from starlette.responses import JSONResponse
from app.database import Database
from app.dependencies import get_settings
from app.routers import user_routes
from app.utils.api_description import getDescription

from fastapi.responses import JSONResponse
from fastapi.requests import Request
import traceback

app = FastAPI(
    title="User Management",
    description=getDescription(),
    version="0.0.1",
    debug=True,
    contact={
        "name": "API Support",
        "url": "http://www.example.com/support",
        "email": "support@example.com",
    },
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
)

@app.get("/")
async def root():
	return {"message": "User Management API is running."}

@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    Database.initialize(settings.database_url, settings.debug)

@app.exception_handler(Exception)
async def exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"message": "An unexpected error occurred."})

app.include_router(user_routes.router)

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        tb = traceback.format_exc()
        print("\n=== EXCEPTION TRACEBACK ===\n")
        print(tb)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "trace": tb}
        )



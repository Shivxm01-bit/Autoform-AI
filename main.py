"""FastAPI application entry point for Google Forms Automation service."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models.schemas import GenerateLinkRequest, GenerateLinkResponse
from services.auth_service import get_current_user
from services.google_form_service import GoogleFormService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("api")

# Service instance
form_service = GoogleFormService()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for application startup and shutdown events."""
    logger.info("Starting Google Forms Automation Service...")
    yield
    logger.info("Shutting down Google Forms Automation Service...")


app = FastAPI(
    title="Google Forms Autofill & Link Generator API",
    description=(
        "FastAPI backend that parses Google Forms and automatically creates "
        "pre-filled links or submission payloads from student profiles."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Enable CORS for web frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
async def root() -> Dict[str, str]:
    """API welcome and health check endpoint."""
    return {
        "status": "online",
        "service": "Google Forms Automation API",
        "version": "1.0.0",
        "documentation": "/docs",
    }


@app.get("/health", tags=["General"])
async def health_check() -> Dict[str, str]:
    """Liveness probe."""
    return {"status": "healthy"}


@app.post(
    "/api/generate-link",
    response_model=GenerateLinkResponse,
    status_code=status.HTTP_200_OK,
    tags=["Form Automation"],
    summary="Generate a pre-filled Google Form link from a student profile",
    response_description="Returns the pre-filled URL and detailed matching breakdown.",
)
async def generate_prefilled_link(
    request: GenerateLinkRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> GenerateLinkResponse:
    """
    Accepts a public Google Form URL and a student profile JSON payload.
    Requires a valid Supabase JWT Bearer token in the Authorization header.

    - Verifies the user's Supabase authentication credentials.
    - Fetches and parses the Google Form structure and question entry IDs using async HTTP (`httpx`).
    - Validates data via Pydantic schemas.
    - Matches student profile fields to form questions using semantic keyword heuristics and custom mappings.
    - Generates a pre-filled Google Form URL (`/viewform?usp=pp_url&entry.xxx=yyy`) ready for opening or submission.
    """
    try:
        user_id = current_user.get("sub", "unknown")
        user_email = current_user.get("email", "unknown")
        logger.info(f"Processing generate-link for user {user_email} ({user_id}) - Form URL: {request.form_url}")
        result = await form_service.generate_prefilled_link(request)
        return result
    except ValueError as val_err:
        logger.warning(f"Validation or fetch error: {val_err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err)
        ) from val_err
    except Exception as exc:
        logger.exception(f"Unexpected error while generating prefilled link: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while parsing the Google Form: {str(exc)}"
        ) from exc


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

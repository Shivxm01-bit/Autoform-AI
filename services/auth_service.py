"""Supabase JWT authentication service and FastAPI dependency."""

import os
import logging
from typing import Any, Dict, Optional
import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger("auth")

# Security scheme for FastAPI OpenAPI docs (Swagger UI)
security_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="Supabase JWT Bearer",
    description="Provide a valid Supabase JWT token in the format: `Bearer <token>`"
)


class SupabaseAuth:
    """Handles verification and extraction of Supabase user tokens."""

    def __init__(self):
        self.jwt_secret = os.getenv("SUPABASE_JWT_SECRET", "").strip()
        self.supabase_url = os.getenv("SUPABASE_URL", "").strip()
        self.algorithm = "HS256"

    def reload_config(self) -> None:
        """Reload configuration from environment variables."""
        self.jwt_secret = os.getenv("SUPABASE_JWT_SECRET", "").strip()
        self.supabase_url = os.getenv("SUPABASE_URL", "").strip()

    def verify_jwt(self, token: str) -> Dict[str, Any]:
        """
        Verify a Supabase JWT token and return decoded claims.

        Raises:
            HTTPException: 401 Unauthorized on invalid/expired token or 500 if secret missing.
        """
        secret = os.getenv("SUPABASE_JWT_SECRET", "").strip() or self.jwt_secret

        if not secret:
            logger.error("SUPABASE_JWT_SECRET is not configured in backend environment (.env)")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "Backend authentication is not configured. "
                    "Please set SUPABASE_JWT_SECRET in your server .env file."
                )
            )

        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                secret,
                algorithms=[self.algorithm],
                options={"verify_aud": False}  # Supabase tokens may have 'authenticated' or custom aud
            )

            # Ensure 'sub' (User ID) is present
            if not payload.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token claims: missing subject identifier.",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return payload

        except jwt.ExpiredSignatureError as err:
            logger.warning(f"Expired JWT token: {err}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication token has expired. Please sign in again.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from err
        except jwt.InvalidTokenError as err:
            logger.warning(f"Invalid JWT token: {err}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid authentication token: {str(err)}",
                headers={"WWW-Authenticate": "Bearer"},
            ) from err
        except Exception as exc:
            logger.error(f"Unexpected token verification error: {exc}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to authenticate credentials.",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc


auth_service = SupabaseAuth()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme)
) -> Dict[str, Any]:
    """
    FastAPI dependency that extracts and validates the Supabase JWT Bearer token.
    Returns the authenticated user's JWT payload dictionary.
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a Bearer token in the Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    user_payload = auth_service.verify_jwt(token)
    return user_payload

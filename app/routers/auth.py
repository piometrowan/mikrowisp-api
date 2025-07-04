from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from datetime import timedelta
import logging

from app.dependencies.auth import auth_service
from app.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBasic()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    is_admin: bool = False
    client_id: int = None


# Base de datos simple en memoria (en producción usar base de datos real)
fake_users_db = {
    "admin": {
        "username": "admin",
        "password": "admin123",  # En producción, usar hash
        "email": "admin@mikrowisp.com",
        "is_admin": True,
        "client_id": None
    },
    "demo": {
        "username": "demo",
        "password": "demo123",
        "email": "demo@mikrowisp.com",
        "is_admin": False,
        "client_id": 1
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica contraseña (simplificado para demo)"""
    # En producción usar bcrypt o similar
    return plain_password == hashed_password


def authenticate_user(username: str, password: str):
    """Autentica usuario"""
    user = fake_users_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: HTTPBasicCredentials = Depends(security)):
    """Endpoint de login que retorna JWT token"""
    user = authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )

    access_token_expires = timedelta(seconds=settings.jwt_expiration)
    access_token = auth_service.create_access_token(
        data={
            "sub": user["username"],
            "email": user["email"],
            "is_admin": user["is_admin"],
            "client_id": user["client_id"]
        },
        expires_delta=access_token_expires
    )

    logger.info(f"Usuario {user['username']} autenticado exitosamente")

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_expiration
    }


@router.post("/register", response_model=dict)
async def register_user(user_data: UserCreate):
    """Registra un nuevo usuario (solo para demo)"""
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El usuario ya existe"
        )

    fake_users_db[user_data.username] = {
        "username": user_data.username,
        "password": user_data.password,  # En producción, hashear
        "email": user_data.email,
        "is_admin": user_data.is_admin,
        "client_id": user_data.client_id
    }

    logger.info(f"Usuario {user_data.username} registrado exitosamente")

    return {"message": "Usuario registrado exitosamente"}


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: dict = Depends(auth_service.verify_token)):
    """Obtiene información del usuario actual"""
    return {
        "username": current_user["sub"],
        "email": current_user.get("email"),
        "is_admin": current_user.get("is_admin", False),
        "client_id": current_user.get("client_id")
    }
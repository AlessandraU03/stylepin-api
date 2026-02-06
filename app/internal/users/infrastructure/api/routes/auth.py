from fastapi import APIRouter, Depends, status
from app.internal.users.application.schemas.auth_schema import RegisterRequest, LoginRequest, AuthResponse
from app.internal.users.application.use_cases.create_user import CreateUserUseCase
from app.internal.users.application.use_cases.login_user import LoginUserUseCase
from app.internal.users.infrastructure.api.dependencies import (
    get_create_user_use_case,
    get_login_user_use_case
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account in StylePin",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "username": "fashionista",
                            "full_name": "Maria Lopez",
                            "bio": None,
                            "avatar_url": None,
                            "preferred_styles": ["Casual", "Minimalista"],
                            "is_verified": False,
                            "created_at": "2024-02-05T10:30:00",
                            "total_pins": 0,
                            "total_followers": 0,
                            "total_following": 0
                        },
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        400: {"description": "Invalid request body or weak password"},
        409: {"description": "Email or username already in use"}
    }
)
async def register(
    request: RegisterRequest,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case)
):
    """
    **Register a new user**
    
    - **username**: Unique username (3-30 characters, alphanumeric)
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars, uppercase, lowercase, number)
    - **full_name**: User's full name
    - **gender**: Optional (male, female, non_binary, prefer_not_to_say)
    - **preferred_styles**: Optional list of fashion styles
    
    Returns user profile and JWT token
    """
    return await use_case.execute(request)

@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and return JWT token",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "username": "fashionista",
                            "full_name": "Maria Lopez",
                            "bio": "Fashion lover 👗✨",
                            "avatar_url": "https://example.com/avatar.jpg",
                            "preferred_styles": ["Casual", "Minimalista"],
                            "is_verified": False,
                            "created_at": "2024-02-05T10:30:00",
                            "total_pins": 42,
                            "total_followers": 156,
                            "total_following": 89
                        },
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer"
                    }
                }
            }
        },
        401: {
            "description": "Invalid credentials, account locked, or account deactivated"
        }
    }
)
async def login(
    request: LoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case)
):
    """
    **Authenticate user**
    
    - **email**: User's email address
    - **password**: User's password
    
    **Security features:**
    - Account locks after 5 failed attempts (15 minutes)
    - Checks if account is active
    - Returns JWT token valid for 7 days
    
    Returns user profile and JWT token
    """
    return await use_case.execute(request)
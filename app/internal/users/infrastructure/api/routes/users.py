from fastapi import APIRouter, Depends, status
from app.internal.users.domain.entities.user import UserProfile, UserMe
from app.internal.users.application.use_cases.get_user import GetUserByIdUseCase
from app.internal.users.infrastructure.api.dependencies import (
    get_user_by_id_use_case,
    get_current_user
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/me",
    response_model=UserMe,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get authenticated user's profile (includes private info like email)",
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "fashionista",
                        "email": "user@stylepin.com",
                        "full_name": "Maria Lopez",
                        "bio": "Fashion lover 👗✨",
                        "avatar_url": "https://example.com/avatar.jpg",
                        "gender": "female",
                        "preferred_styles": ["Casual", "Minimalista"],
                        "is_verified": False,
                        "role": "user",
                        "created_at": "2024-02-05T10:30:00",
                        "last_login": "2024-02-05T15:45:00"
                    }
                }
            }
        },
        401: {"description": "Not authenticated"}
    }
)
async def get_me(
    current_user: UserMe = Depends(get_current_user)
):
    """
    **Get current authenticated user**
    
    Returns complete profile including:
    - Public information (username, name, bio, avatar)
    - Private information (email)
    - Preferences (gender, styles)
    - Account status (verified, role)
    - Timestamps
    
    **Requires authentication** (Bearer token)
    """
    return current_user

@router.get(
    "/{user_id}",
    response_model=UserProfile,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Get public profile of any user by their ID",
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
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
                    }
                }
            }
        },
        404: {"description": "User not found"}
    }
)
async def get_user_by_id(
    user_id: str,
    use_case: GetUserByIdUseCase = Depends(get_user_by_id_use_case)
):
    """
    **Get public user profile**
    
    Returns only public information:
    - Username and full name
    - Bio and avatar
    - Preferred styles
    - Verification status
    - Statistics (pins, followers, following)
    
    **Does NOT include:**
    - Email
    - Password
    - Login attempts
    - Private settings
    
    **No authentication required**
    """
    return await use_case.execute(user_id)
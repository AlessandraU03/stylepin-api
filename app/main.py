from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import logging

from core.database.config import settings
from core.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    AccountLockedException,
    AccountDeactivatedException,
    UserNotFoundException,
    UnauthorizedException,
)
from core.connection import engine, Base

# ── Importar modelos para que SQLAlchemy los registre ─────────
from core.database.models import (
    UserModel,
    PinModel,
    BoardModel,
    BoardPinModel,
    BoardCollaboratorModel,
    LikeModel,
    FollowModel,
    CommentModel,
)

# ── Importar routers ──────────────────────────────────────────
from internal.users.infrastructure.http.auth_routes import router as auth_router
from internal.users.infrastructure.http.user_routes import router as users_router
from internal.pines.infrastructure.http.pin_routes import router as pins_router
from internal.boards.infrastructure.http.board_routes import router as boards_router
from internal.likes.infrastructure.http.like_routes import router as likes_router
from internal.follows.infrastructure.http.follow_routes import router as follows_router
from internal.comments.infrastructure.http.comment_routes import router as comments_router

# ── Upload de imágenes ────────────────────────────────────────
from core.upload_routes import router as upload_router

# ── WebSocket ─────────────────────────────────────────────────
from core.websocket_routes import router as ws_router

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== LIFESPAN EVENTS ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Amura API...")
    if settings.DEBUG:
        logger.info("🗄️ Creating database tables...")
        Base.metadata.create_all(bind=engine)
    yield
    logger.info("👋 Shutting down Amura API...")


# ==================== APP ====================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## 📌 Amura API - Tu Pinterest Personal de Moda

    API REST para gestionar perfiles de usuario, pins de moda y crear una comunidad fashion.

    ### 🎯 Features Principales:

    * **Autenticación segura** con JWT
    * **Gestión de usuarios** (registro, login, perfiles)
    * **Pins de moda** (crear, editar, eliminar, feed, trending)
    * **Boards** (tableros con colaboradores)
    * **Sistema social** (follows, likes, comments)
    * **Upload de imágenes** (Cloudinary)
    * **WebSocket** (notificaciones en tiempo real)

    ### 🔐 Autenticación:

    1. Registrarse en `/api/v1/auth/register`
    2. Hacer login en `/api/v1/auth/login`
    3. Copiar el token recibido
    4. Click en el botón **"Authorize"** (🔓) arriba a la derecha
    5. Pegar el token
    6. ¡Listo! Ya puedes acceder a endpoints protegidos

    ### 📸 Upload de imágenes:

    1. `POST /api/v1/upload/pin-image` → sube imagen y obtiene URL
    2. `POST /api/v1/pins` → crea pin usando la URL obtenida

    ### 🔌 WebSocket:

    ```
    ws://localhost:3000/ws?token=<JWT_TOKEN>
    ```

    ### 📚 Documentación:

    * **Swagger UI**: `/docs`
    * **ReDoc**: `/redoc`

    ---

    **Materia**: Programación para Móviles I
    **Periodo**: Enero-Abril 2026
    """,
    contact={
        "name": "Amura Support",
        "email": "support@amura.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


# ==================== MIDDLEWARE ====================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ==================== EXCEPTION HANDLERS ====================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": errors,
        },
    )


@app.exception_handler(UserAlreadyExistsException)
async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "User Already Exists", "message": exc.detail},
    )


@app.exception_handler(InvalidCredentialsException)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Invalid Credentials", "message": exc.detail},
    )


@app.exception_handler(AccountLockedException)
async def account_locked_handler(request: Request, exc: AccountLockedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Account Locked", "message": exc.detail},
    )


@app.exception_handler(AccountDeactivatedException)
async def account_deactivated_handler(request: Request, exc: AccountDeactivatedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Account Deactivated", "message": exc.detail},
    )


@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "User Not Found", "message": exc.detail},
    )


@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Unauthorized", "message": exc.detail},
    )


# ==================== ROUTES ====================

# Health check
@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    status_code=status.HTTP_200_OK,
)
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(pins_router, prefix="/api/v1")
app.include_router(boards_router, prefix="/api/v1")
app.include_router(likes_router, prefix="/api/v1")
app.include_router(follows_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.include_router(upload_router, prefix="/api/v1")

# WebSocket router (sin prefix — se conecta en ws://host/ws)
app.include_router(ws_router)


# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
)
async def root():
    return {
        "message": "Welcome to Amura API! 📌",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "websocket": "ws://localhost:3000/ws?token=<JWT_TOKEN>",
    }
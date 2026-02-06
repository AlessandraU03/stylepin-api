from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import logging

from app.core.config import settings
from app.core.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    AccountLockedException,
    AccountDeactivatedException,
    UserNotFoundException,
    UnauthorizedException
)
from app.internal.users.infrastructure.database.connection import engine, Base
from app.internal.users.infrastructure.api.routes import auth, users

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== LIFESPAN EVENTS ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja eventos de inicio y cierre de la aplicación
    """
    # Startup
    logger.info("🚀 Starting StylePin API...")
    logger.info(f"📚 Swagger UI: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"📖 ReDoc: http://{settings.HOST}:{settings.PORT}/redoc")
    
    # Crear tablas si no existen (solo en desarrollo)
    if settings.DEBUG:
        logger.info("🗄️  Creating database tables...")
        Base.metadata.create_all(bind=engine)
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down StylePin API...")

# ==================== APP INSTANCE ====================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## 📌 StylePin API - Tu Pinterest Personal de Moda
    
    API REST para gestionar perfiles de usuario, pins de moda y crear una comunidad fashion.
    
    ### 🎯 Features Principales:
    
    * **Autenticación segura** con JWT
    * **Gestión de usuarios** (registro, login, perfiles)
    * **Pins de moda** (Corte 2)
    * **Sistema social** (follows, likes, saves) (Corte 2)
    * **Recomendaciones IA** (Corte 3)
    
    ### 🔐 Autenticación:
    
    1. Registrarse en `/api/v1/auth/register`
    2. Hacer login en `/api/v1/auth/login`
    3. Copiar el token recibido
    4. Click en el botón **"Authorize"** (🔓) arriba a la derecha
    5. Pegar token en el formato: `Bearer <tu-token>`
    6. ¡Listo! Ya puedes acceder a endpoints protegidos
    
    ### 📚 Documentación:
    
    * **Swagger UI**: Interfaz interactiva para probar endpoints
    * **ReDoc**: Documentación alternativa más limpia
    
    ### 👥 Desarrolladores:
    
    * Tu nombre
    * Nombre de tu compañero
    
    ---
    
    **Materia**: Programación para Móviles I  
    **Institución**: Tu universidad  
    **Periodo**: Enero-Abril 2026
    """,
    contact={
        "name": "StylePin Support",
        "email": "support@stylepin.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
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
    """Maneja errores de validación de Pydantic"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": errors
        }
    )

@app.exception_handler(UserAlreadyExistsException)
async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "User Already Exists", "message": exc.detail}
    )

@app.exception_handler(InvalidCredentialsException)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Invalid Credentials", "message": exc.detail}
    )

@app.exception_handler(AccountLockedException)
async def account_locked_handler(request: Request, exc: AccountLockedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Account Locked", "message": exc.detail}
    )

@app.exception_handler(AccountDeactivatedException)
async def account_deactivated_handler(request: Request, exc: AccountDeactivatedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Account Deactivated", "message": exc.detail}
    )

@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "User Not Found", "message": exc.detail}
    )

@app.exception_handler(UnauthorizedException)
async def unauthorized_handler(request: Request, exc: UnauthorizedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Unauthorized", "message": exc.detail}
    )

# ==================== ROUTES ====================

# Health check
@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if API is running",
    status_code=status.HTTP_200_OK
)
async def health_check():
    """
    **Health check endpoint**
    
    Returns API status and version
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")

# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    summary="API Root",
    description="Welcome message and API info"
)
async def root():
    """
    **API Root**
    
    Returns welcome message and links to documentation
    """
    return {
        "message": "Welcome to StylePin API! 📌",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }
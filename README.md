# 📌 StylePin API - Tu Pinterest Personal de Moda

API REST desarrollada con **FastAPI**, **MySQL** y **Arquitectura Hexagonal** para gestionar una red social de moda.

## 🎯 Características

- ✅ Autenticación JWT segura
- ✅ Registro y Login de usuarios
- ✅ Perfiles públicos y privados
- ✅ Arquitectura Hexagonal (Clean Architecture)
- ✅ Swagger UI integrado
- ✅ Validaciones con Pydantic
- ✅ Protección contra ataques (bloqueo de cuenta)
- ✅ CORS configurado
- ✅ Manejo de errores centralizado

## 🚀 Instalación y Ejecución

### 1️⃣ Clonar repositorio
```bash
git clone <tu-repo>
cd stylepin-api
```

### 2️⃣ Crear entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar variables de entorno
```bash
# Copiar .env.example a .env
cp .env.example .env

# Editar .env con tus credenciales de MySQL
# Cambiar DB_PASSWORD por tu contraseña
```

### 5️⃣ Crear base de datos
```bash
# Conectar a MySQL
mysql -u root -p

# Ejecutar script de migración
source migrations/init.sql

# O manualmente:
# CREATE DATABASE stylepin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6️⃣ Correr API
```bash
python run.py
```

### 7️⃣ Abrir Swagger UI
```
http://localhost:8000/docs
```

## 📚 Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🧪 Testing con Swagger

### Flujo completo:

1. **Registro**:
   - Ir a `POST /api/v1/auth/register`
   - Click en "Try it out"
   - Llenar datos de ejemplo
   - Click en "Execute"
   - **Copiar el token** de la respuesta

2. **Autenticación**:
   - Click en botón **"Authorize"** 🔓 (arriba a la derecha)
   - Pegar: `Bearer {tu-token-aqui}`
   - Click en "Authorize"
   - Click en "Close"

3. **Probar endpoint protegido**:
   - Ir a `GET /api/v1/users/me`
   - Click en "Try it out"
   - Click en "Execute"
   - ✅ Verás tu perfil completo

## 📂 Estructura del Proyecto
```
stylepin-api/
├── app/
│   ├── core/              # Configuración y seguridad
│   ├── domain/            # Entidades y contratos
│   ├── application/       # Casos de uso y DTOs
│   └── infrastructure/    # Implementaciones (DB, API)
├── migrations/            # Scripts SQL
├── tests/                 # Tests unitarios
├── .env                   # Variables de entorno
├── requirements.txt       # Dependencias
└── run.py                 # Script para correr
```

## 🔐 Seguridad

- Contraseñas hasheadas con **bcrypt**
- Tokens **JWT** con expiración
- Bloqueo de cuenta después de **5 intentos fallidos**
- Validaciones estrictas con **Pydantic**
- Separación de entidades públicas/privadas

## 🛣️ Endpoints Disponibles

### Autenticación

- `POST /api/v1/auth/register` - Registrar usuario
- `POST /api/v1/auth/login` - Iniciar sesión

### Usuarios

- `GET /api/v1/users/me` - Obtener perfil propio (requiere auth)
- `GET /api/v1/users/{user_id}` - Obtener perfil público

## 🔄 Roadmap

### Corte 1 (Actual) ✅
- Login + Register
- Gestión de usuarios

### Corte 2 (Próximo)
- CRUD de Pins
- Sistema de follows
- Likes y saves
- Tableros (boards)

### Corte 3 (Final)
- Recomendaciones IA
- Búsqueda avanzada
- Analytics
- Integración shopping

## 👥 Autores

- **Tu Nombre** - Autenticación y arquitectura
- **Nombre Compañero** - Pins y features

## 📄 Licencia

MIT License
# StylePin API 🚀

> Backend REST API para StylePin — red social visual de moda. Construida con Python, FastAPI y MySQL, desplegada en AWS EC2 con Docker.

---

## ¿Qué es StylePin?

StylePin es una red social visual donde los usuarios pueden inspirarse, armar outfits y compartirlos con la comunidad. Esta API provee todos los servicios que consume la app Android: autenticación JWT, gestión de pins, tableros colaborativos, interacción social (likes, comentarios, follows), notificaciones push via FCM y comunicación en tiempo real via WebSocket.

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.10 |
| Framework | FastAPI |
| Base de datos | MySQL 8 |
| ORM | SQLAlchemy |
| Autenticación | JWT (HS256) con `python-jose` |
| Push Notifications | Firebase Admin SDK (FCM) |
| Imágenes | Cloudinary |
| Tiempo real | WebSocket nativo FastAPI |
| Contenedores | Docker + Docker Compose |
| Reverse Proxy | Caddy (HTTPS automático) |
| Infraestructura | AWS EC2 (Ubuntu 24.04) |

---

## Arquitectura

La API sigue **Clean Architecture** con separación estricta de capas:

```
app/
├── main.py                  # Punto de entrada FastAPI
├── core/
│   ├── connection.py        # Sesión SQLAlchemy
│   └── database/
│       └── models.py        # Modelos ORM (SQLAlchemy)
│
└── internal/
    ├── auth/
    │   ├── domain/          # Entidades + interfaces de repositorio
    │   ├── application/     # Casos de uso (login, register, refresh)
    │   └── infrastructure/  # Controladores HTTP, middlewares JWT, adaptadores MySQL
    ├── pins/
    ├── boards/
    ├── likes/
    ├── follows/
    ├── comments/
    ├── notifications/
    └── users/
```

Cada módulo interno sigue la misma estructura:
```
feature/
├── domain/
│   ├── entities/            # Dataclasses de dominio
│   └── repository/          # Interfaces abstractas
├── application/
│   └── use_cases/           # Lógica de negocio pura
└── infrastructure/
    ├── adapters/             # Implementaciones MySQL (SQLAlchemy)
    ├── http/                 # Routes + Controllers (FastAPI)
    └── dependencies.py      # Inyección de dependencias (FastAPI Depends)
```

---

## Endpoints disponibles

Base URL: `https://stylepin.ddns.net/api/v1`

### 🔐 Auth
| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/auth/register` | Registro de nuevo usuario |
| `POST` | `/auth/login` | Login con email/contraseña → JWT |
| `POST` | `/auth/refresh` | Renovar token JWT |
| `GET` | `/auth/me` | Perfil del usuario autenticado |

### 📌 Pins
| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/pins` | Listar pins públicos (paginado) |
| `POST` | `/pins` | Crear pin (multipart/form-data con imagen) |
| `GET` | `/pins/{pin_id}` | Obtener pin por ID |
| `PUT` | `/pins/{pin_id}` | Editar pin |
| `DELETE` | `/pins/{pin_id}` | Eliminar pin |
| `GET` | `/pins/search` | Buscar pins por texto |
| `GET` | `/pins/user/{user_id}` | Pins de un usuario |

### 🗂️ Boards
| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/boards` | Listar tableros públicos |
| `POST` | `/boards` | Crear tablero |
| `GET` | `/boards/{board_id}` | Obtener tablero |
| `PUT` | `/boards/{board_id}` | Editar tablero |
| `DELETE` | `/boards/{board_id}` | Eliminar tablero |
| `GET` | `/boards/user/{user_id}` | Tableros de un usuario |
| `POST` | `/boards/{board_id}/pins` | Agregar pin al tablero |
| `DELETE` | `/boards/{board_id}/pins/{pin_id}` | Quitar pin del tablero |
| `GET` | `/boards/{board_id}/pins` | Pins de un tablero |
| `POST` | `/boards/{board_id}/collaborators` | Agregar colaborador |
| `DELETE` | `/boards/{board_id}/collaborators/{user_id}` | Quitar colaborador |
| `PUT` | `/boards/{board_id}/collaborators/{user_id}` | Actualizar permisos de colaborador |
| `GET` | `/boards/{board_id}/collaborators` | Listar colaboradores |

### ❤️ Likes
| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/likes` | Toggle like a un pin |
| `GET` | `/likes/status/{pin_id}` | Estado de like del usuario autenticado |
| `GET` | `/likes/pins/{pin_id}` | Usuarios que dieron like a un pin |

### 💬 Comments
| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/comments` | Crear comentario o respuesta |
| `GET` | `/comments/pin/{pin_id}` | Comentarios de un pin |
| `PUT` | `/comments/{comment_id}` | Editar comentario |
| `DELETE` | `/comments/{comment_id}` | Eliminar comentario |
| `POST` | `/comments/{comment_id}/like` | Dar like a un comentario |

### 👥 Follows
| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/follows` | Seguir a un usuario |
| `DELETE` | `/follows/{user_id}` | Dejar de seguir |
| `GET` | `/follows/{user_id}/followers` | Seguidores de un usuario |
| `GET` | `/follows/{user_id}/following` | Usuarios que sigue |
| `GET` | `/follows/{user_id}/counts` | Contadores de seguidores/seguidos |
| `GET` | `/follows/status/{user_id}` | Estado de follow con otro usuario |

### 🔔 Notifications
| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/notifications` | Historial de notificaciones del usuario |
| `PUT` | `/notifications/{notification_id}/read` | Marcar como leída |
| `GET` | `/notifications/test` | Enviar notificación de prueba |

### 👤 Users
| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/users/{user_id}` | Perfil público de un usuario |
| `PUT` | `/users/me` | Editar perfil propio |
| `POST` | `/users/fcm-token` | Registrar token FCM del dispositivo |
| `GET` | `/users/search` | Buscar usuarios por nombre/username |

### ⚡ WebSocket
| Endpoint | Descripción |
|---|---|
| `wss://stylepin.ddns.net/ws?token=JWT` | Conexión en tiempo real para alertas |

---

## Autenticación

Todos los endpoints (excepto `/auth/register` y `/auth/login`) requieren el header:

```
Authorization: Bearer <token_jwt>
```

El token se obtiene en `POST /auth/login` y tiene expiración configurable. Si expira, usa `POST /auth/refresh`.

---

## Modelos de base de datos

```sql
users           — id, username, email, password_hash, full_name, bio, avatar_url, role
pins            — id, user_id, image_url, title, description, category, season, likes_count
boards          — id, user_id, name, is_private, is_collaborative, pins_count
board_pins      — id, board_id, pin_id, user_id, notes
board_collaborators — id, board_id, user_id, can_edit, can_add_pins, can_remove_pins
likes           — id, user_id, pin_id
follows         — id, follower_id, following_id
comments        — id, pin_id, user_id, text, parent_comment_id, likes_count
notifications   — id, user_id, actor_id, type, title, body, is_read
fcm_tokens      — id, user_id, device_token, device_name, is_active
```

---

## Instalación y despliegue

### Requisitos

- Docker y Docker Compose instalados
- Dominio con DNS apuntando al servidor (para HTTPS automático con Caddy)
- Cuenta de Firebase con `serviceAccountKey.json`
- Cuenta de Cloudinary

### 1. Clonar el repositorio

```bash
git clone https://github.com/AlessandraU03/stylepin-api.git
cd stylepin-api
```

### 2. Variables de entorno

Crea un archivo `.env` en la raíz:

```env
# Base de datos
DB_HOST=db
DB_PORT=3306
DB_NAME=stylepin
DB_USER=stylepin_user
DB_PASSWORD=tu_password_seguro

# JWT
SECRET_KEY=tu_clave_secreta_muy_larga
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Cloudinary
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret

# Firebase
FIREBASE_CREDENTIALS_PATH=/app/serviceAccountKey.json
```

### 3. Firebase

Coloca tu archivo `serviceAccountKey.json` en la raíz del proyecto.

### 4. Levantar con Docker Compose

```bash
docker-compose up -d --build
```

Esto levanta 3 servicios:
- **api** — FastAPI en puerto 8000
- **caddy** — Reverse proxy con HTTPS automático en puertos 80/443
- **db** — MySQL 8 (opcional si usas una DB externa)

### 5. Verificar

```bash
docker ps
docker logs stylepin-api_api_1 --tail 50
```

La documentación interactiva estará disponible en:
- Swagger UI: `https://tu-dominio/docs`
- ReDoc: `https://tu-dominio/redoc`

---

## Despliegue en producción (AWS EC2)

El servidor de producción corre en una instancia EC2 de AWS (Ubuntu 24.04). El flujo de despliegue es:

```bash
# En el servidor EC2
cd ~/stylepin-api
git fetch origin
git pull origin correciones
docker-compose down
docker-compose up -d --build
```

Caddy gestiona automáticamente los certificados SSL/TLS con Let's Encrypt.

---

## Flujo de notificaciones push

```
Evento (like / follow / comment)
    └── Use Case guarda Notification en tabla notifications
            └── Use Case obtiene FCM token del usuario destino
                    └── Firebase Admin SDK envía push notification
                            └── App Android recibe en FirebaseMessagingService
```

Los tipos de notificación soportados son: `like`, `follow`, `comment`, `board_collaboration`.

---

## Documentación interactiva

La API incluye documentación Swagger completa en:

```
https://stylepin.ddns.net/docs
```

---

## Repositorios relacionados

- **Backend API (este repositorio):** [stylepin-api](https://github.com/AlessandraU03/stylepin-api)
- **App Android (Kotlin/Compose):** [Stylepin-App](https://github.com/AlessandraU03/Stylepin-App)

---

## Desarrollado por

**Alessandra Ulloa** — [@AlessandraU03](https://github.com/AlessandraU03)
**Alhan Velasco** — [@alhan-velasco](https://github.com/alhan-velasco)
---

*StylePin — Viste el mundo a tu manera* 📌

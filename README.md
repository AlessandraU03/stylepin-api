# StylePin — Android App 📌

> Red social visual para amantes de la moda. Inspírate, arma tus outfits y compártelos con la comunidad.

---

## ¿Qué es StylePin?

StylePin resuelve la fragmentación de contenido en plataformas generalistas como Pinterest o Instagram, donde los outfits se mezclan con decoración, memes y publicidad irrelevante. StylePin ofrece un feed dedicado **100% a ropa y estilo**, con herramientas de curaduría en tableros, interacción social completa, sincronización inteligente en segundo plano y notificaciones push en tiempo real.

---

## Características principales

- 🏠 **Feed de moda** — LazyVerticalStaggeredGrid cargado instantáneamente desde Room (SSoT)
- 📌 **Pins** — Crea y comparte outfits con imagen (galería o cámara), categoría, temporada, precio y link de compra
- 🗂️ **Tableros** — Organiza pins en colecciones públicas o privadas, con modo colaborativo
- ❤️ **Likes optimistas** — El corazón responde al instante y revierte si falla la red
- 💬 **Comentarios** — Interacción en tiempo real en la vista de detalle de cada pin
- 👥 **Comunidad** — Sigue usuarios, ve seguidores y seguidos
- 🔔 **Notificaciones push** — FCM para likes, seguidores y comentarios
- 🔍 **Explorar** — Busca pins y usuarios
- 🌙 **Modo oscuro / claro** — Soporte completo con Material Design 3
- 🔐 **Login biométrico** — Huella dactilar o FaceID (Hardware 1)
- 📷 **Cámara nativa** — Captura imágenes directamente al crear pins (Hardware 3)
- 🔦 **Flash LED** — Parpadea al iniciar sesión exitosamente (Hardware 2)
- ☁️ **Sincronización en segundo plano** — WorkManager cada 12 horas con restricciones de Wi-Fi y batería

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Kotlin 2.x |
| UI | Jetpack Compose + Material Design 3 |
| Arquitectura | Clean Architecture + MVVM |
| Inyección de dependencias | Hilt (Dagger 2) |
| Navegación | Navigation Compose (type-safe routes con `@Serializable`) |
| Persistencia local | Room v2 + TypeConverters Gson |
| HTTP | Retrofit 2 + OkHttp + AuthInterceptor JWT |
| Imágenes | Coil |
| Background | WorkManager + `@HiltWorker` + `@AssistedInject` |
| Push notifications | Firebase Cloud Messaging (FCM) |
| Tiempo real | WebSocket (OkHttp) con `MutableSharedFlow` |
| Biometría | `BiometricPrompt` |
| Cámara | `ActivityResultContracts.TakePicture()` + `FileProvider` |

---

## Arquitectura

```
app/
├── core/
│   ├── di/                  # Módulos Hilt globales (Network, Database, Hardware)
│   ├── navigation/          # Rutas type-safe (@Serializable)
│   ├── network/             # AuthInterceptor, WebSocketManager, FCMService
│   └── data/local/          # AppDatabase, Room DAOs
│
└── features/
    ├── auth/                # Login, Register, Biometría
    ├── pins/                # Feed, Detalle, Crear, Editar
    ├── boards/              # Tableros, Detalle, Colaboradores
    ├── explore/             # Búsqueda de pins y usuarios
    ├── profile/             # Perfil propio, edición, configuración
    ├── community/           # Seguidores y seguidos
    └── notifications/       # Historial de notificaciones
```

Cada feature sigue la estructura:
```
feature/
├── data/
│   ├── datasources/remote/  # API interfaces (Retrofit), DTOs, Mappers
│   ├── datasources/local/   # DAO, Entities, Mappers
│   └── repositories/        # Implementación del repositorio
├── domain/
│   ├── entities/            # Modelos de dominio
│   ├── repository/          # Interfaz del repositorio
│   └── usecases/            # Casos de uso
└── presentation/
    ├── screens/             # Composables
    ├── viewmodels/          # ViewModels + UiState
    └── components/          # Componentes reutilizables
```

---

## Flujo de datos reactivo

```
Room (PinDao)
    └── Flow<List<PinEntity>>
            └── PinRepositoryImpl.getPinsFlow()
                    └── PinsViewModel (colecta con launchIn)
                            └── StateFlow<PinsUiState>
                                    └── PinsScreen (collectAsStateWithLifecycle)
```

Al llamar `refreshPins()`, Retrofit descarga la lista, la inserta en Room con `REPLACE`, y Room notifica automáticamente a todos los colectores activos — sin polling manual.

---

## Patrón de actualización optimista

```kotlin
fun toggleLike(pinId: String) {
    val pin = _uiState.value.pinDetail ?: return
    val currentLiked = pin.isLikedByMe
    // 1. Actualizar UI al instante
    _uiState.update { state ->
        state.copy(pinDetail = pin.copy(
            isLikedByMe = !currentLiked,
            likesCount = pin.likesCount + if (currentLiked) -1 else 1
        ))
    }
    viewModelScope.launch {
        // 2. Petición real al servidor
        toggleLikeUseCase(pinId, currentLiked).onFailure {
            // 3. Revertir si falla
            _uiState.update { state -> state.copy(pinDetail = pin) }
        }
    }
}
```

---

## Requisitos previos

- Android Studio Hedgehog o superior
- JDK 21
- Android SDK 36 (minSdk 26)
- Cuenta de Firebase con un proyecto configurado
- Archivo `google-services.json` colocado en `app/`
- Archivo `local.properties` con las variables de entorno (ver abajo)

---

## Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/AlessandraU03/Stylepin-App.git
cd Stylepin-App
```

### 2. Configurar variables de entorno

Crea o edita `local.properties` en la raíz del proyecto:

```properties
BASE_URL_STYLEPIN=https://stylepin.ddns.net/
```

### 3. Agregar Firebase

Descarga `google-services.json` desde tu consola de Firebase y colócalo en `app/google-services.json`.

### 4. Compilar

```bash
./gradlew assembleDev       # Build de desarrollo
./gradlew assembleProd      # Build de producción
```

O directamente desde Android Studio con el flavor `dev` o `prod`.

---

## Product Flavors

| Flavor | Descripción |
|---|---|
| `dev` | Nombre de app: **StylePin (DEV)** — para desarrollo y pruebas |
| `prod` | Nombre de app: **StylePin** — para producción |

---

## WorkManager — Sincronización

| Modalidad | Frecuencia | Restricciones |
|---|---|---|
| Automática | Cada 12 horas | Solo Wi-Fi + batería no baja |
| Manual | Al instante | Sin restricciones |

La sincronización manual está disponible en **Configuración → Sincronización de pines**.

El worker usa `@HiltWorker` + `@AssistedInject` para inyección limpia del `PinsRepository`. Requiere deshabilitar el inicializador por defecto de WorkManager en `AndroidManifest.xml`:

```xml
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false"
    tools:node="merge">
    <meta-data
        android:name="androidx.work.WorkManagerInitializer"
        android:value="androidx.startup"
        tools:node="remove" />
</provider>
```

---

## Notificaciones Push FCM — Flujo completo

```
Login exitoso
    └── LoginViewModel solicita token FCM
            └── POST /api/v1/users/fcm-token
                    └── Backend guarda token en tabla fcm_tokens

Evento (like / follow / comment)
    └── Backend obtiene token del usuario destino
            └── Firebase Admin SDK envía push
                    └── StylePinFirebaseMessagingService.onMessageReceived()
                            └── NotificationChannel → pantalla de bloqueo / pantalla Notificaciones
```

---

## Retos técnicos resueltos

| Problema | Solución |
|---|---|
| KSP falla con Room + Hilt en funciones DAO que retornan `Unit` | Cambiar `clearAll()` de `Unit` a `Int` (filas eliminadas) |
| WorkManager no inyecta dependencias con `@Inject` estándar | Usar `@HiltWorker` + `@AssistedInject` + `HiltWorkerFactory` en `StylePinApp` |
| HTTP 307 Redirect pierde el header `Authorization` | Eliminar trailing slash de la URL en `NotificationApi.kt` |
| SQLite no soporta columnas de tipo array | `TypeConverters` con Gson para serializar `List<String>` a JSON |
| Estado de like inconsistente entre UI y servidor | Sets estáticos `localLikedPins` como fuente de verdad local durante la sesión |

---

## Repositorios relacionados

- **Backend API (Python/FastAPI):** [stylepin-api](https://github.com/AlessandraU03/stylepin-api)
- **App Android (este repositorio):** [Stylepin-App](https://github.com/AlessandraU03/Stylepin-App)

---

## Desarrollado por

**Alessandra Ulloa** — [@AlessandraU03](https://github.com/AlessandraU03)
**Alhan Velasco** — [@alhan-velasco]((https://github.com/alhan-velasco))

---

*StylePin — Viste el mundo a tu manera* 📌

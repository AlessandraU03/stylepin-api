"""
Servicio de subida de imágenes a Cloudinary
"""
import cloudinary
import cloudinary.uploader
import logging
from typing import Optional
from fastapi import UploadFile

from core.database.config import settings

logger = logging.getLogger(__name__)

# Configurar Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

# Tipos de imagen permitidos
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class ImageUploadService:
    """Servicio para subir y eliminar imágenes en Cloudinary"""

    @staticmethod
    async def upload_image(
        file: UploadFile,
        folder: str = "pins",
        max_size: int = MAX_FILE_SIZE,
    ) -> dict:
        """
        Sube una imagen a Cloudinary.
        """
        # Validar tipo de archivo
        if file.content_type not in ALLOWED_TYPES:
            raise ValueError(
                f"Tipo de archivo no permitido: {file.content_type}. "
                f"Permitidos: {', '.join(ALLOWED_TYPES)}"
            )

        # Leer contenido
        content = await file.read()

        # Validar tamaño
        if len(content) > max_size:
            raise ValueError(
                f"Archivo demasiado grande: {len(content) / (1024*1024):.1f}MB. "
                f"Máximo: {max_size / (1024*1024):.0f}MB"
            )

        try:
            # Subir a Cloudinary
            result = cloudinary.uploader.upload(
                content,
                folder=f"amura/{folder}",
                resource_type="image",
                quality="auto",
                fetch_format="auto",
            )

            logger.info(f"✅ Image uploaded: {result['secure_url']}")

            return {
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "width": result.get("width", 0),
                "height": result.get("height", 0),
                "format": result.get("format", ""),
                "size_bytes": result.get("bytes", 0),
            }

        except Exception as e:
            logger.error(f"❌ Error uploading image: {e}")
            raise ValueError(f"Error al subir imagen: {str(e)}")

    @staticmethod
    async def delete_image(public_id: str) -> bool:
        """Elimina una imagen de Cloudinary."""
        try:
            result = cloudinary.uploader.destroy(public_id)
            success = result.get("result") == "ok"
            if success:
                logger.info(f"🗑️ Image deleted: {public_id}")
            return success
        except Exception as e:
            logger.error(f"❌ Error deleting image: {e}")
            return False

    @staticmethod
    def get_thumbnail_url(url: str, width: int = 300, height: int = 300) -> str:
        """Genera URL de thumbnail desde una URL de Cloudinary."""
        if "cloudinary.com" not in url:
            return url
        return url.replace(
            "/upload/",
            f"/upload/c_fill,w_{width},h_{height}/",
        )


# Instancia global
image_service = ImageUploadService()
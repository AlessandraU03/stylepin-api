"""
Dependencias de Notificaciones
"""
from internal.notifications.infrastructure.http.notification_controller import NotificationController


def get_notification_controller() -> NotificationController:
    """Obtener el controlador de notificaciones"""
    return NotificationController()
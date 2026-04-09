import firebase_admin
from firebase_admin import credentials, messaging
from app.core.database.config import settings
import os
import json
from pathlib import Path

def init_firebase():
    """Inicializar Firebase Admin SDK"""
    try:
        # Verificar si Firebase ya está inicializado
        try:
            firebase_admin.get_app()
            return
        except ValueError:
            pass

        # Cargar credenciales desde archivo JSON
        firebase_key_path = Path(__file__).parent.parent / "config" / "firebase.json"
        
        if not firebase_key_path.exists():
            raise FileNotFoundError(f"Firebase key file not found at {firebase_key_path}")

        cred = credentials.Certificate(str(firebase_key_path))
        firebase_admin.initialize_app(cred)
        print("✓ Firebase initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing Firebase: {str(e)}")
        raise

def send_fcm_notification(device_tokens: list, title: str, body: str, data: dict = None) -> dict:
    """
    Enviar notificación push mediante FCM
    
    Args:
        device_tokens: Lista de tokens FCM del dispositivo
        title: Título de la notificación
        body: Cuerpo de la notificación
        data: Datos adicionales (diccionario)
    
    Returns:
        Resultado del envío
    """
    try:
        if not device_tokens:
            return {"success": False, "message": "No device tokens provided"}

        payload_data = data or {}
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data=payload_data,
            tokens=device_tokens,
        )

        response = messaging.send_multicast(message)
        
        result = {
            "success": True,
            "successful": response.successful,
            "failed": response.failed,
            "message": f"Sent to {response.successful} devices, {response.failed} failed"
        }
        
        return result
    except Exception as e:
        print(f"Error sending FCM notification: {str(e)}")
        return {"success": False, "error": str(e)}

# Inicializar Firebase cuando se importa el módulo
init_firebase()
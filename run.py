import sys
import os

# Agregar 'app' al path para que los imports internos funcionen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

import uvicorn
from app.core.database.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
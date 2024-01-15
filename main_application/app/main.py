from fastapi import FastAPI
from app.room.router import room_router
from app.client.router import client_router
from app.reservation.router import reservation_router

from app.repository.utils import *

# Создаём объект FastAPI
app = FastAPI()

# Подлючаемся к базам данных
app.add_event_handler("startup", startup_handling)
app.add_event_handler("shutdown", shutdown_handling)

# Регестрируем routers
app.include_router(room_router)
app.include_router(client_router)
app.include_router(reservation_router)

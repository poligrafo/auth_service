from fastapi import FastAPI

from app.api.deps import engine
from app.api.v1 import auth, users
from app.core.logging_config import setup_logging
from app.models import Base

# Инициализируем логирование
logger = setup_logging()

app = FastAPI(title="Сервис Авторизации")

# Создание таблиц при запуске (можно убрать после миграций)
Base.metadata.create_all(bind=engine)
logger.info("Запуск приложения и создание таблиц, если необходимо.")

# Включение маршрутизаторов API
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])


@app.get("/")
def read_root():
    return {"message": "Сервис Авторизации работает"}

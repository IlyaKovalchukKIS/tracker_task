from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi_users import FastAPIUsers
from src.schemas import UserRead, UserCreate, User as UserSchemas
from src.repositories.crud import get_user_manager, auth_backend
from src.repositories import db_helper
from src.repositories.models import Task, User
from src.routing.task import task_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создание таблиц перед запуском приложения"""
    async with db_helper.engine.begin() as conn:
        # await conn.run_sync(Task.metadata.drop_all)
        await conn.run_sync(User.metadata.create_all)
        await conn.run_sync(Task.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)
fastapi_users = FastAPIUsers[UserSchemas, int](
    get_user_manager,
    [auth_backend],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(task_router)

if __name__ == "__main__":
    uvicorn.run("src.app:app", reload=True)

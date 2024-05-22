from fastapi import FastAPI
from routers.healtext_nlp import router
from routers.server import server_router
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.admin import router as admin_router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

from typing import Any

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(server_router)
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(admin_router)
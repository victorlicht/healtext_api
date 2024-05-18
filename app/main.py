from fastapi import FastAPI
from routers.healtext_nlp import router
from routers.server import server_router
app = FastAPI()
app.include_router(router)
app.include_router(server_router)
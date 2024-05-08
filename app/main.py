from fastapi import FastAPI
from routers.healtext_nlp import router
app = FastAPI()
app.include_router(router)
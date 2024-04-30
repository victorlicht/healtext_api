from fastapi import FastAPI
from routers.uploads import router
app = FastAPI()
app.include_router(router)
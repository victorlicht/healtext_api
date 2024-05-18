from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi import status


server_router = APIRouter()

@server_router.get("/")
async def server():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Server Running Successfully",
        },
        media_type="application/json"
    )

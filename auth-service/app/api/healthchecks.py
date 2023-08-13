from fastapi import APIRouter
from starlette.responses import JSONResponse

router = APIRouter()


@router.get("/")
async def healthcheck() -> JSONResponse:
    return JSONResponse({"status": "ok"})

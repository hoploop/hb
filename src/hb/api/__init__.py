from starlette.requests import Request

from hb.clients.mongodb import AsyncMongodbClient
from fastapi import HTTPException
from starlette import status
from starlette.requests import Request


async def get_database(request: Request = None) -> AsyncMongodbClient:
    database: AsyncMongodbClient = request.app.state.database
    return database


def not_found(msg: str):
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=msg,
        headers={"WWW-Authenticate": "Basic"},
    )


def unauthorized(msg: str):
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=msg,
        headers={"WWW-Authenticate": "Basic"},
    )


def generic_error(msg: str):
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=msg,
        headers={"WWW-Authenticate": "Basic"},
    )

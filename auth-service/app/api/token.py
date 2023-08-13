from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.exceptions import UserNotFoundError, WrongPasswordError
from app.schemas import (
    TokenSchema,
)
from app.use_cases.token import AuthenticateUserUseCase

router = APIRouter()


@router.post("/", response_model=TokenSchema)
async def generate_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: AuthenticateUserUseCase = Depends(AuthenticateUserUseCase),
) -> TokenSchema:
    try:
        return await use_case.execute(form_data.username, form_data.password)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        ) from e
    except WrongPasswordError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Wrong password"
        ) from e

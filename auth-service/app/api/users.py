from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from app.exceptions import UserAlreadyExistsError, UserNotFoundError
from app.schemas import (
    CreateUserRequestSchema,
    UpdateUserRequestSchema,
    UserSchema,
)
from app.use_cases.users import CreateUserUseCase, UpdateUserUseCase, get_current_user

router = APIRouter()


@router.post("/", response_model=UserSchema)
async def create_user(
    data: CreateUserRequestSchema,
    use_case: CreateUserUseCase = Depends(CreateUserUseCase),
) -> UserSchema:
    try:
        return await use_case.execute(data)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="User with the same username or email already exists",
        ) from e


@router.get("/me", response_model=UserSchema)
async def get_user(
    user: UserSchema = Depends(get_current_user),
) -> UserSchema:
    return user.model_dump(mode="json")


@router.patch("/me", response_model=UserSchema)
async def update_user(
    data: UpdateUserRequestSchema,
    user: UserSchema = Depends(get_current_user),
    use_case: UpdateUserUseCase = Depends(UpdateUserUseCase),
) -> UserSchema:
    try:
        return await use_case.execute(user, data)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="User with the same username or email already exists",
        ) from e
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        ) from e

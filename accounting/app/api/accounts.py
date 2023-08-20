from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.constants import Role
from app.exceptions import (
    AccountNotFoundError,
)
from app.schemas import AccountSchema, TransactionSchema, UserSchema
from app.use_cases.accounts import (
    GetTransactionsUseCase,
    GetUserAccountsUseCase,
    GetUserAccountUseCase,
)
from app.use_cases.users import get_current_user

router = APIRouter()


@router.get("/accounts", response_model=list[AccountSchema])
async def get_accounts(
    user: UserSchema = Depends(get_current_user),
    use_case: GetUserAccountsUseCase = Depends(GetUserAccountsUseCase),
) -> list[AccountSchema]:
    if user.role not in (Role.ADMIN, Role.ACCOUNTANT):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Only accountants and administrators can see all accounts",
        )

    return await use_case.execute()


@router.get("/accounts/{account_id}", response_model=AccountSchema)
async def get_account(
    account_id: UUID | str,
    user: UserSchema = Depends(get_current_user),
    use_case: GetUserAccountUseCase = Depends(GetUserAccountUseCase),
):
    try:
        return await use_case.execute(account_id, user)
    except AccountNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Account not found",
        )


@router.get(
    "/accounts/{account_id}/transactions", response_model=list[TransactionSchema]
)
async def get_account_transactions(
    account_id: UUID | str,
    user: UserSchema = Depends(get_current_user),
    use_case: GetTransactionsUseCase = Depends(GetTransactionsUseCase),
):
    try:
        return await use_case.execute(account_id, user)
    except AccountNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Account not found",
        )

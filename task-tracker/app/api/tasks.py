from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.constants import Role
from app.exceptions import (
    OnlyAssignedUserCanCompleteTaskError,
    TaskNotFoundError,
    UserNotFoundError,
)
from app.schemas import CreateTaskRequestSchema, TaskSchema, UserSchema
from app.use_cases.tasks import (
    CompleteTaskUseCase,
    CreateTaskUseCase,
    GetTasksUseCase,
    GetTaskUseCase,
    ShuffleTasksUseCase,
)
from app.use_cases.users import get_current_user

router = APIRouter()


@router.post("/", response_model=TaskSchema)
async def create_task(
    data: CreateTaskRequestSchema,
    _: UserSchema = Depends(get_current_user),
    use_case: CreateTaskUseCase = Depends(CreateTaskUseCase),
) -> TaskSchema:
    try:
        return await use_case.execute(data)
    except UserNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Task executor not found",
        )


@router.get("/", response_model=list[TaskSchema])
async def get_tasks(
    user: UserSchema = Depends(get_current_user),
    use_case: GetTasksUseCase = Depends(GetTasksUseCase),
) -> list[TaskSchema]:
    return await use_case.execute(user)


@router.get("/{task_id}", response_model=TaskSchema)
async def get_task(
    task_id: UUID,
    user: UserSchema = Depends(get_current_user),
    use_case: GetTaskUseCase = Depends(GetTaskUseCase),
) -> TaskSchema:
    try:
        return await use_case.execute(task_id, user)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Task not found",
        )


@router.post("/{task_id}/complete", response_model=TaskSchema)
async def complete_task(
    task_id: UUID,
    user: UserSchema = Depends(get_current_user),
    use_case: CompleteTaskUseCase = Depends(CompleteTaskUseCase),
) -> TaskSchema:
    try:
        return await use_case.execute(task_id, user)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Task not found",
        )
    except OnlyAssignedUserCanCompleteTaskError:
        if user.role in (Role.ADMIN, Role.MANAGER):
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN,
                detail="Only the assigned user can complete the task",
            )
        else:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Task not found",
            )


@router.post("/shuffle", response_model=list[TaskSchema])
async def shuffle_tasks(
    user: UserSchema = Depends(get_current_user),
    use_case: ShuffleTasksUseCase = Depends(ShuffleTasksUseCase),
) -> list[TaskSchema]:
    if user.role not in (Role.ADMIN, Role.MANAGER):
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Only managers and administrators can shuffle tasks",
        )

    return await use_case.execute()

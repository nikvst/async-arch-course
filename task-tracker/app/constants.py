import enum


class Role(enum.Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    WORKER = "worker"
    MANAGER = "manager"


class UserEvent(str, enum.Enum):
    USER_CREATED = "Users.Created"
    USER_UPDATED = "Users.Updated"
    USER_ROLE_CHANGED = "Users.RoleChanged"


class TaskEvent(str, enum.Enum):
    # CUD
    TASK_CREATED = "Tasks.Created"
    TASK_UPDATED = "Tasks.Updated"

    # business events
    TASK_NEW_TASK_CREATED = "Tasks.NewTaskCreated"
    TASK_ASSIGNED = "Tasks.Assigned"
    TASK_COMPLETED = "Tasks.Completed"

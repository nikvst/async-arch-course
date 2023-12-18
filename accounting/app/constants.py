import enum


class Role(enum.Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    WORKER = "worker"
    MANAGER = "manager"


class UserEvent(str, enum.Enum):
    USER_CREATED = "Users.Created"
    USER_UPDATED = "Users.Updated"


class TaskEvent(str, enum.Enum):
    TASK_NEW_TASK_CREATED = "Tasks.NewTaskCreated"
    TASK_ASSIGNED = "Tasks.Assigned"
    TASK_COMPLETED = "Tasks.Completed"


class TransactionEvent(str, enum.Enum):
    TRANSACTION_CREATED = "Transactions.Created"

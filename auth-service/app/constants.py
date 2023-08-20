import enum


class Role(str, enum.Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    WORKER = "worker"
    MANAGER = "manager"


class UserEvent(str, enum.Enum):
    USER_CREATED = "Users.Created"
    USER_UPDATED = "Users.Updated"
    USER_ROLE_CHANGED = "Users.RoleChanged"

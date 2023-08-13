import enum


class Role(enum.Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    WORKER = "worker"
    MANAGER = "manager"


class UserEvent(str, enum.Enum):
    USER_CREATED = "UserCreated"
    USER_UPDATED = "UserUpdated"
    USER_DELETED = "UserDeleted"
    USER_ROLE_CHANGED = "UserRoleChanged"

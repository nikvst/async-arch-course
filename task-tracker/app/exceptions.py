class UserNotFoundError(Exception):
    pass


class TaskNotFoundError(Exception):
    pass


class OnlyAssignedUserCanCompleteTaskError(Exception):
    pass

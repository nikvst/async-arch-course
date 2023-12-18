class UserNotFoundError(Exception):
    pass


class AccountNotFoundError(Exception):
    pass


class OnlyAssignedUserCanCompleteTaskError(Exception):
    pass

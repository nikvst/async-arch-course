from sqladmin import ModelView

from app.models import Account, Transaction, User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.is_active]
    is_async = True

    can_create = False
    can_edit = False
    can_delete = False


class AccountAdmin(ModelView, model=Account):
    column_list = [Account.id, Account.user, Account.balance]
    is_async = True

    can_create = False
    can_edit = False
    can_delete = False


class TransactionAdmin(ModelView, model=Transaction):
    column_list = [
        Transaction.id,
        Transaction.user,
        Transaction.debt,
        Transaction.credit,
        Transaction.created_at,
    ]
    is_async = True

    can_create = False
    can_edit = False
    can_delete = False

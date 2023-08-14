from sqladmin import ModelView

from app.models import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.is_active]
    is_async = True

    can_create = False
    can_edit = False
    can_delete = False

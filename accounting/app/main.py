from fastapi import FastAPI
from sqladmin import Admin

from app.admin import AccountAdmin, TransactionAdmin, UserAdmin

# from app.api.accounts import router as accounts_router
from app.api.healthchecks import router as healthcheck_router
from app.db import engine

app = FastAPI(title="UberPopug accounting service")

# TODO: yep, we need a12n for admin panel.
admin = Admin(app, engine)
admin.add_view(UserAdmin)
admin.add_view(AccountAdmin)
admin.add_view(TransactionAdmin)

app.include_router(healthcheck_router, prefix="/healthcheck", tags=["healthcheck"])
# app.include_router(accounts_router, prefix="/", tags=["accounts"])

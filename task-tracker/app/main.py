from fastapi import FastAPI
from sqladmin import Admin

from app.admin import UserAdmin
from app.api.healthchecks import router as healthcheck_router
from app.api.tasks import router as tasks_router
from app.db import engine

app = FastAPI(title="UberPopug auth service")

# TODO: yep, we need a12n for admin panel.
admin = Admin(app, engine)
admin.add_view(UserAdmin)

app.include_router(healthcheck_router, prefix="/healthcheck", tags=["healthcheck"])
app.include_router(tasks_router, prefix="/tasks", tags=["tasks"])

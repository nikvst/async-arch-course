from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqladmin import Admin

from app.admin import UserAdmin
from app.api.healthchecks import router as healthcheck_router
from app.api.token import router as token_router
from app.api.users import router as users_router
from app.db import engine

app = FastAPI(title="UberPopug auth service")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: yep, we need a12n for admin panel.
admin = Admin(app, engine)
admin.add_view(UserAdmin)

app.include_router(healthcheck_router, prefix="/healthcheck", tags=["healthcheck"])
app.include_router(token_router, prefix="/token", tags=["token"])
app.include_router(users_router, prefix="/users", tags=["users"])

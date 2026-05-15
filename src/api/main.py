from fastapi import FastAPI
from src.api.v1.routers.posts import router as posts_router
# from src.api.v1.routers.users import router as users_router  # подключит другой чел

app = FastAPI(
    title="Ads Manager API",
    version="1.0.0",
)

API_V1_PREFIX = "/api/v1"

app.include_router(posts_router, prefix=API_V1_PREFIX)
# app.include_router(users_router, prefix=API_V1_PREFIX)
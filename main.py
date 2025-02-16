from fastapi import FastAPI
import uvicorn
from lifespan import lifespan
from routes.clothes_routes import router as clothes_routes
from routes.auth_routes import router as auth_router
from routes.user_routes import router as user_router

app = FastAPI(
    title="ClothesAPI",
    version='1.0.0',
    lifespan=lifespan
)

app.include_router(clothes_routes)
app.include_router(user_router)
app.include_router(auth_router)

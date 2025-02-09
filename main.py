from fastapi import FastAPI
import uvicorn
from lifespan import lifespan
from routes.GET_routes import router as GET_routes

app = FastAPI(
    title="ClothesAPI",
    version='1.0.0',
    lifespan=lifespan
)

app.include_router(GET_routes)

from fastapi import FastAPI
from routes.GET_routes import router as GET_routes

app = FastAPI(
    title="ClothesAPI",
    version='1.0.0'
)

app.include_router(GET_routes)
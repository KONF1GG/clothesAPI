from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

@router.get('/')
async def root():
    return {"message": "hello"}
    

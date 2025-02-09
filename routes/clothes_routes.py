from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import uuid
from pathlib import Path
import aiofiles
from dependencies import SessionDependency
from models import Clothes, User
from schemas import ItemId, NewClothes

router = APIRouter()

UPLOAD_FOLDER = "uploaded_images"
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)  # Создаем папку, если не существует

@router.post('/v1/clothes', response_model=ItemId)
async def add_clothes(
    session: SessionDependency,
    clothes_item: str = Form(..., description="JSON string representing the clothes item. Example: {'name': 'shirt', 'type_id': 1, 'user_id': 123}"), 
    file: UploadFile = File(..., description="The image file representing the clothes item."),
):
    try:
        clothes_item_data = NewClothes.parse_raw(clothes_item)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid clothes_item data: {str(e)}"
        )

    user = await session.get(User, clothes_item_data.user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    file_name = f"{uuid.uuid4().hex}.jpg"
    file_location = Path(UPLOAD_FOLDER) / file_name

    async with aiofiles.open(file_location, 'wb') as f:
        await f.write(await file.read())

    new_clothes = Clothes(
        name=clothes_item_data.name,
        type_id=clothes_item_data.type_id,
        user_id=clothes_item_data.user_id,
        image_url=str(file_location)
    )

    try:
        session.add(new_clothes)
        await session.commit()
        await session.refresh(new_clothes)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error creating clothes: {str(e)}"
        )

    return ItemId(id=new_clothes.id)

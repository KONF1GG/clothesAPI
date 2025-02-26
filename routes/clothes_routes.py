import json
import os
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import uuid
from pathlib import Path
import aiofiles
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from config import UPLOAD_FOLDER
from dependencies import SessionDependency, TokenDependency
from models import Clothes, ClothesType, User
from schemas import ClothesModel, ClothesModelAll, ClothesTypeModel, ItemId, NewClothes, UpdateClothes
import crud
from sqlalchemy.orm import selectinload

router = APIRouter()



@router.post('/v1/wardrobe', response_model=ItemId)
async def add_clothes(
    session: SessionDependency,
    token: TokenDependency,
    clothes_item: str = Form(..., description='JSON string with clothes data. Example: {"name": "shirt", "type_id": 22, "user_id": 1}'), 
    file: UploadFile = File(..., description="Image file representing the clothes item."),
):
    """Добавление новой одежды"""
    try:
        clothes_item_data = NewClothes.parse_raw(clothes_item)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid clothes_item data: {str(e)}")

    user = await crud.get_item(session, User, clothes_item_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")


    file_name = f"{uuid.uuid4().hex}.jpg"
    file_location = Path(UPLOAD_FOLDER) / file_name
    print(file_location)

    try:
        async with aiofiles.open(file_location, 'wb') as f:
            await f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    new_clothes = Clothes(
        name=clothes_item_data.name,
        type_id=clothes_item_data.type_id,
        user_id=clothes_item_data.user_id,
        image_url=str(file_name)
    )

    new_clothes = await crud.add_item(session, new_clothes)
    return ItemId(id=new_clothes.id)

# Получение всех вещей пользователя
@router.get('/v1/wardrobes', response_model=list[ClothesModel])
async def get_wardrobe(session: SessionDependency, user_id: int):
    """Получить список вещей пользователя с данными о типе одежды."""
    result = await session.execute(select(Clothes).join(ClothesType).where(Clothes.user_id == user_id).options(selectinload(Clothes.type)))
    clothes = result.unique().scalars().all()

    return [
        ClothesModel(
            id=item.id,
            name=item.name,
            user_id=item.user_id,
            type=ClothesTypeModel( 
                id=item.type.id,
                name=item.type.name,
                category=item.type.category,
            ),
            url=item.image_url,
        )
        for item in clothes
    ]
@router.get('/v1/wardrobe', response_model=ClothesModelAll)
async def get_clothes(session: SessionDependency, token: TokenDependency, clothes_id: int):
    """Получить данные по определенной вещи с типом одежды"""
    query = (
        select(Clothes)
        .options(joinedload(Clothes.type))
        .where(Clothes.id == clothes_id)
    )

    result = await session.execute(query)
    item = result.unique().scalar_one_or_none()  

    if not item:
        raise HTTPException(status_code=404, detail=f"Clothes not found with id {clothes_id}")

    return ClothesModelAll(
        id=item.id,
        name=item.name,
        type=item.type.name, 
        url=item.image_url,
        category=item.type.category,
        user_id=item.user_id,
    )


# @router.get('/v1/wardrobe/image/{clothes_id}')
# async def get_clothes_image(clothes_id: int, token: TokenDependency, session: SessionDependency):
#     """Получить изображение вещи по её ID."""
#     clothes = await crud.get_item(session, Clothes, clothes_id)
#     if not clothes:
#         raise HTTPException(status_code=404, detail="Clothes not found")

#     image_path = Path(clothes.image_url)
#     if not image_path.exists():
#         raise HTTPException(status_code=404, detail="Image not found")

#     return FileResponse(image_path)

@router.delete('/v1/wardrobe/{clothes_id}', response_model=ItemId)
async def delete_clothes(clothes_id: int, session: SessionDependency, token: TokenDependency):
    """Удалить вещь и её изображение"""
    clothes = await crud.get_item(session, Clothes, clothes_id)
    if not clothes:
        raise HTTPException(status_code=404, detail="Clothes not found")

    image_path = Path(clothes.image_url)
    if image_path.exists():
        image_path.unlink()

    await crud.delete_item(session, Clothes, clothes_id)
    return ItemId(id=clothes_id)

@router.patch('/v1/wardrobe/{clothes_id}', response_model=ClothesModelAll)
async def update_clothes_data(
    session: SessionDependency, 
    token: TokenDependency,
    clothes_id: int,
    clothes_data: UpdateClothes
):
    """Частичное обновление данных одежды (без изображения)."""
    item = await crud.get_item(session, Clothes, clothes_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clothes not found")

    for field, value in clothes_data.dict(exclude_unset=True).items():
        setattr(item, field, value)

    await session.commit()
    await session.refresh(item)

    return ClothesModelAll(
        id=item.id,
        name=item.name,
        type=item.type.name, 
        url=item.image_url,
        category=item.type.category,
        user_id=item.user_id,
    )



@router.patch('/v1/wardrobe/image/{clothes_id}', response_model=ClothesModelAll)
async def update_clothes_image(
    session: SessionDependency, 
    token: TokenDependency,
    clothes_id: int,
    file: Optional[UploadFile] = File(None)
):
    """Обновление изображения вещи."""
    item = await crud.get_item(session, Clothes, clothes_id)
    if not item:
        raise HTTPException(status_code=404, detail="Clothes not found")

    if not file:
        raise HTTPException(status_code=400, detail="No image file provided.")

    file_name = f"{uuid.uuid4().hex}.jpg"
    file_location = Path(UPLOAD_FOLDER) / file_name

    async with aiofiles.open(file_location, 'wb') as f:
        await f.write(await file.read())

    item.image_url = str(file_location)

    await session.commit()
    await session.refresh(item)

    return ClothesModelAll(
        id=item.id,
        name=item.name,
        type=item.type.name, 
        category=item.type.category,
        user_id=item.user_id,
    )

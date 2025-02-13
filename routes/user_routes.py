from typing import List, Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

import auth, crud
from dependencies import SessionDependency, TokenDependency
from schemas import (
    ItemId, CreateUser, ResponseUserData, UpdateUser, StatusResponse, UserModel
)
from models import User, Token

router = APIRouter()

@router.get("/v1/users", response_model=List[UserModel]) 
async def get_users(session: SessionDependency, token: TokenDependency):
    """Эндпоинт для получения списка пользователей"""
    query = select(User)
    result = await session.execute(query)
    users = result.scalars().unique().all()

    return [UserModel(id=user.id, username=user.username, firstname=user.firstname, lastname=user.lastname) for user in users]

@router.post('/v1/user', response_model=ItemId)
async def create_user(
        user_data: CreateUser,
        session: SessionDependency,
        token: TokenDependency
):
    """Эндпоинт для создания нового пользователя"""
    user = User(**user_data.dict())
    user.password = await auth.hash_password(user_data.password)
    user = await crud.add_item(session, user)
    return {'id': user.id}

@router.get('/v1/user/{user_id}', response_model=ResponseUserData)
async def get_user(
    user_id: int,
    session: SessionDependency,
    token: TokenDependency
):
    """Эндпоинт для получения данных пользователя"""
    user = await crud.get_item(session, User, user_id)
    return ResponseUserData(id=user.id, username=user.username, firstname=user.firstname, lastname=user.lastname)

@router.patch('/v1/user/{user_id}', response_model=ItemId)
async def update_user(
        user_data: UpdateUser,
        user_id: int,
        session: SessionDependency,
        token: TokenDependency
):
    """Эндпоинт для обновления пользователя"""
    user = await crud.get_item(session, User, user_id)

    for field, value in user_data.dict(exclude_unset=True).items():
        if field == "password":
            value = await auth.hash_password(value)
        setattr(user, field, value)

    await session.commit()

    return {'id': user.id}

@router.delete('/v1/user/{user_id}', response_model=StatusResponse)
async def delete_user(user_id: int, session: SessionDependency, token: TokenDependency):
    """Эндпоинт для удаления пользователя"""
    user = await crud.get_item(session, User, user_id)

    # Удаляем токены пользователя
    await session.execute(delete(Token).where(Token.user_id == user.id))

    # Удаляем пользователя
    await session.execute(delete(User).where(User.id == user.id))

    await session.commit()
    return {'status': 'deleted'}

from sqlite3 import IntegrityError
from fastapi import HTTPException
from models import ORM_CLASS, ORM_OBJECT
from sqlalchemy.ext.asyncio import AsyncSession


async def add_item(session: AsyncSession, item: ORM_OBJECT) -> ORM_OBJECT:
    """Добавляет объект в базу данных."""
    session.add(item)
    try:
        await session.commit()
    except IntegrityError as err:
        if err.orig.pgcode == '23505':
            raise HTTPException(status_code=409, detail='Item already exists')
        raise err
    return item


async def get_item(session: AsyncSession, orm_class: ORM_CLASS, item_id: int) -> ORM_OBJECT:  # type: ignore
    """Получает объект по его ID."""
    orm_obj = await session.get(orm_class, item_id)
    if orm_obj is None:
        raise HTTPException(status_code=404, detail=f'{orm_class.__name__} not found with id {item_id}')
    return orm_obj


async def delete_item(session: AsyncSession, orm_class: ORM_CLASS, item_id: int) -> None: # type: ignore
    """Удаляет объект по его ID."""
    item = await get_item(session, orm_class, item_id)
    await session.delete(item)
    await session.commit()

from sqlite3 import IntegrityError

from fastapi import HTTPException
from models import ORM_OBJECT
from sqlalchemy.ext.asyncio import AsyncSession


async def add_item(session: AsyncSession, item: ORM_OBJECT) -> ORM_OBJECT:
    session.add(item)
    try:
        await session.commit()
    except IntegrityError as err:
        if err.orig.pgcode == '23505':
            raise HTTPException(status_code=409, detail='Item already exists')
        raise err
    return item


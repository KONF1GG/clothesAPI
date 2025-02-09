from typing import Annotated

from fastapi import Depends
from models import Session


async def get_session():
    async with Session() as session:
        yield session

SessionDependency = Annotated[Session, Depends(get_session, use_cache=True)]
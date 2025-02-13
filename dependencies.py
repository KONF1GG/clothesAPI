import datetime
from typing import Annotated, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, HTTPException, Header
from models import Session, Token
import config


async def get_session() -> AsyncSession:
    async with Session() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session, use_cache=True)]


async def get_token(session: SessionDependency, x_token: Optional[str] = Header(None)) -> Token:
    if x_token is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    token_query = select(Token).where(
        Token.token == x_token,
        Token.creation_time >= datetime.datetime.now() - datetime.timedelta(seconds=int(config.TOKEN_TTL))
    )
    token = await session.scalar(token_query)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    else:
        return token


TokenDependency = Annotated[Token, Depends(get_token)]

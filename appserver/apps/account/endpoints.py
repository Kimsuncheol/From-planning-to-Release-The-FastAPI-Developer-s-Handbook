from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select, SQLModel
from appserver.db import create_async_engine, create_session
from .models import User
from appserver.db import DbSessionDep


router = APIRouter(prefix="/account")

@router.get("/users/{username}")
async def user_detail(username: str, session: DbSessionDep) -> User:
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is not None:
        return user
    # dsn = "sqlite+aiosqlite:///./test.db"
    # engine = create_async_engine(dsn)
    # async with engine.connect() as conn:
    #     await conn.run_sync(SQLModel.metadata.drop_all)
    #     await conn.run_sync(SQLModel.metadata.create_all)
    #     await conn.commit()

    # session_factory = create_session(engine)

    # async with session_factory() as session:
    #     stmt = select(User).where(User.username == username)
    #     result = await session.execute(stmt)
    #     user = result.scalar_one_or_none()

    # if user:
    #     return user


    # if username == "test":
    #     return {
    #         "id": 1,
    #         "username": username,
    #         "email": f"{username}@example.com",
    #         "display_name": username,
    #         "is_host": True,
    #         "created_at": datetime.now(timezone.utc),
    #         "updated_at": datetime.now(timezone.utc),
    #     }

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


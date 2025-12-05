import pytest
from appserver.db import create_async_engine, create_session
from appserver.apps.account import models
from appserver.apps.calendar import models
from sqlmodel import SQLModel

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from appserver.db import create_async_engine, create_session, use_session
from appserver.app import include_routers

@pytest.fixture(autouse=True)
async def db_session():
    dsn = "sqlite+aiosqlite:///./:memory:"
    # dsn = "sqlite+aiosqlite:///./test.db"
    engine = create_async_engine(dsn)
    async with engine.connect() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    

        session_factory = create_session(engine)
        async with session_factory() as session:
            yield session
        
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.rollback()

    await engine.dispose()
    
@pytest.fixture()
def fastapi_app():
    app = FastAPI()
    include_routers(app)

    async def overrride_use_session():
        yield db_session

    app.dependency_overrides[use_session] = overrride_use_session
    return app
    
# 테스트 클라이언트도 Pytest fixture로 관리한다.
@pytest.fixture()
def client(fastapi_app: FastAPI):
    with TestClient(fastapi_app) as client:
        yield client



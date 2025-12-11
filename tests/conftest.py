import pytest
from appserver.db import create_async_engine, create_session
from appserver.apps.account import models
from appserver.apps.calendar import models
from sqlmodel import SQLModel

from fastapi import FastAPI, status
from appserver.apps.account.schemas import LoginPayload
from sqlalchemy.ext.asyncio import AsyncSession
from appserver.db import create_async_engine, create_session, use_session
from appserver.app import include_routers
from appserver.apps.account.utils import hash_password
from appserver.apps.calendar import models as calendar_models

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

@pytest.fixture()
async def host_user(db_session: AsyncSession):
    user = account_models.User(
        username="puddingcamp",
        hashed_password=hash_password("testtest"),
        email="test@example.com",
        display_name="푸딩캠프",
        is_host=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.flush()
    return user

@pytest.fixture()
def client_with_auth(fastapi_app: FastAPI, host_user: account_models.User):
    payload = LoginPayload.model_validate({
        "username": host_user.username,
        "password": "testtest"
    })

    with TestClient(fastapi_app) as client:
        response = client.post("/account/login", json=payload.model_dump())
        assert response.status_code == status.HTTP_200_OK

        auth_token = response.cookie.get("auth_token")
        assert auth_token is not None

        client.cookie["auth_token"] = auth_token
        yield client
        
@pytest.fixture()
async def guest_user(db_session: AsyncSession):
    user = account_models.User(
        username="puddingcafe",
        hashed_password=hash_password("testtest"),
        email="puddingcafe@example.com",
        display_name="푸딩카페",
        is_host=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.flush()
    return user

@pytest.fixture()
async def host_user_calendar(db_session: AsyncSession, host_user: account_models.User):
    calendar = calendar_models.Calendar(
        topics=["푸딩캠프", "푸딩카페"],
        description="푸딩캠프의 캘린더",
        host_id=host_user.id,
        google_calendar_id="test",
    )
    db_session.add(calendar)
    await db_session.commit()
    await db_session.refresh()
    await db_session.flush()
    return calendar

@pytest.fixture()
def client_with_guest_auth(fastapi_app: FastAPI, guest_user: account_models.User):
    payload = LoginPayload.model_validate({
        "username": guest_user.username,
        "password": "testtest"
    })

    with TestClient(fastapi_app) as client:
        response = client.post("/account/login", json=payload.model_dump())
        assert response.status_code == status.HTTP_200_OK

        auth_token = response.cookie.get("auth_token")
        assert auth_token is not None

        client.cookie["auth_token"] = auth_token
        yield client
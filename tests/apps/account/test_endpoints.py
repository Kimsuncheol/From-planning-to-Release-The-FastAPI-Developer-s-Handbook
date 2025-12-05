from appserver.apps.account.models import User
from appserver.apps.calendar.models import Calendar
from appserver.apps.account.endpoints import user_detail
import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from appserver.app import app
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from appserver.db import create_async_engine, create_session

async def test_user_detail_successfully(db_session: AsyncSession):
    host_user = User(
        username="test_hostuser",
        password="test",
        email="test.hostuser@example.com",
        display_name="test",
        is_host=True,
    )

    db_session.add(host_user)
    await db_session.commit()
    result = await user_detail(host_user.username, db_session)

async def test_user_detail_not_found():
    with pytest.raises(HTTPException) as exc_info:
        await user_detail("not found")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

def test_user_detail_by_http_not_found(client: TestClient):
    response = client.get("/account/users/not_found")

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_user_detail_by_http(client: TestClient):

    response = client.get("/account/users/test")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "test"
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "test"
    assert data["is_host"] is True
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

# dsn = "sqlite+aiosqlite:///./test.db"
# engine = create_async_engine(dsn)

# 데이터베이스에 실재하는 사용자의 상세 정보를 API로 가져오는 것을 확인한다.
# 데이터베이스에 테이블을 만든다.
async def test_user_detail_for_real_user(client: TestClient, db_session: AsyncSession):

    user = User(
        username="test",
        password="test",
        email="test@example.com",
        display_name="test",
        is_host=True,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.flush()
    
    response = client.get(f"/account/users/{user.username}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["display_name"] == user.display_name

    response = client.get("/account/users/not_found")
    assert response.status_code == status.HTTP_404_NOT_FOUND
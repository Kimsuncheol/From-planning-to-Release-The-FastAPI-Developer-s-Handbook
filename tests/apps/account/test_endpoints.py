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

async def test_user_detail_successfully():
    result = await user_detail("test")
    assert result["id"] == 1
    assert result["username"] == "test"
    assert result["email"] == "test@example.com"
    assert result["display_name"] == "test"
    assert result["is_host"] is True
    assert result["created_at"] is not None
    assert result["updated_at"] is not None

async def test_user_detail_not_found():
    with pytest.raises(HTTPException) as exc_info:
        await user_detail("not found")
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

def test_user_detail_by_http_not_found(client: TestClient):
    # client = TestClient(app)
    response = client.get("/account/users/not_found")

    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_user_detail_by_http(client: TestClient):
    # client = TestClient(app)

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
    # async with engine.begin() as conn:      # 생성한 DB 연결 엔진의 접속을 열고(begin()), 이 연결 정보 객체를 이용하여 동기식으로 테이블을 만든다.
    #     await conn.run_sync(SQLModel.metadata.drop_all)   # 메타데이터 객체의 drop_all 함수를 실행하면 메타데이터에 등록된 모든 모델의 테이블을 삭제한다. 이것을 먼저 실행하는 이유는 테스트 DB에 테이블이 찌꺼기처럼 남아 있을 때 이들을 청소하기 위해서이다.
    #     await conn.run_sync(SQLModel.metadata.create_all)   # 메타데이터 객체의 create_all 함수를 실행하면 메타데이터에 등록된 모든 모델의 테이블을 생성한다.
        
    # 세션 팩토리로 세션 객체를 만들고 이 객체로 DB에 데이터를 추가하는 코드
    # session_factory = create_session(engine)

    # async with session_factory() as session:
    #     user = User(
    #         username="test",
    #         password="test",
    #         email="test@example.com",
    #         display_name="test",
    #         is_host=True,
    #     )
    #     session.add(user)
    #     await session.commit()

    user = User(
        username="test",
        password="test",
        email="test@example.com",
        display_name="test",
        is_host=True,
    )

    # client = TestClient(app)
    db_session.add(user)
    await db_session.commit()
    await db_session.flush()
    
    response = client.get(f"/account/users/{user.username}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # assert data["username"] == "test"
    # assert data["email"] == "test@example.com"
    # assert data["display_name"] == "test"
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert data["display_name"] == user.display_name

    response = client.get("/account/users/not_found")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # async with engine.begin() as conn:
    #     await conn.run_sync(SQLModel.metadata.drop_all)
    # await engine.dispose()
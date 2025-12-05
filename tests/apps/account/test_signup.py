import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from appserver.apps.account.endpoints import signup
from appserver.apps.account.models import User
from appserver.apps.account.exceptions import DuplicatedUsernameError, DuplicatedEmailError

async def test_모든_입력_항목을_유효한_값으로_입력하면_계정이_생성된다(client: TestClient, db_session: AsyncSession):
    payload = {
        "username": "test",
        "email": "test@example.com",
        "display_name": "test",       
        "password": "test테스트1234",
    }

    result = await signup(payload, db_session)

    assert isinstance(result, User)
    assert result.username == payload["username"]
    assert result.email == payload["email"]
    assert result.display_name == payload["display_name"]
    assert result.is_host is False
    
    response = client.get(f"/account/users/{payload['username']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["display_name"] == payload["display_name"]
    assert data["is_host"] is False

@pytest.mark.parametrize(
    "username",
    [
        "0123456789012345678901234567890123456789",
        12345678,
        "x"
    ]
)

async def test_사용자명이_유효하지_않으면_사용자명이_유효하지_않다는_메시지를_담은_오류를_일으킨다(
    client: TestClient, 
    db_session: AsyncSession,
    username: str
):
    payload = {
        "username": username,
        "email": "test@example.com",
        "display_name": "test",       
        "password": "test테스트1234",
    }

    # username이 유효하지 않으면 ValidationError가 일으킨다.
    with pytest.raises(ValidationError) as exc:
        await signup(payload, db_session)

async def test_계정_ID가_중복되면_중복_계정_ID_오류를_일으킨다(
    client: TestClient, 
    db_session: AsyncSession
):
    payload = {
        "username": "test",
        "email": "test@example.com",
        "display_name": "test",       
        "password": "test테스트1234",
    }

    await signup(payload, db_session)

    payload["email"] = "test2@example.com"
    # username이 중복되면 DuplicateUsernameError가 일으킨다.
    with pytest.raises(DuplicatedUsernameError) as exc:
        await signup(payload, db_session)

async def test_e_mail_주소가_중복되면_중복_E_mail_주소_오류를_일으킨다(db_session: AsyncSession):
    payload = {
        "username": "test",
        "email": "test@example.com",
        "display_name": "test",       
        "password": "test테스트1234",
    }

    await signup(payload, db_session)

    payload["username"] = "test2"
    # email이 중복되면 DuplicatedEmailError가 일으킨다.
    with pytest.raises(DuplicatedEmailError) as exc:
        await signup(payload, db_session)

async def test_표시명을_입력하지_않으면_무작위_문자열_8글자로_대신한다(db_session: AsyncSession):
    payload = {
        "username": "test",
        "email": "test@example.com",       
        "password": "test테스트1234",
    }

    user = await signup(payload, db_session)

    assert isinstance(user.display_name, str)
    assert len(user.display_name) == 8
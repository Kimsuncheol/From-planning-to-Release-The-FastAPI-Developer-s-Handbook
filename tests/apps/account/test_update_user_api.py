import pytest
from fastapi import status
from fastapi.testclient import TestClient
from appserver.apps.account.models import User
from sqlalchemy.ext.asyncio import AsyncSession

UPDATABLE_FIELDS = frozenset(["display_name", "email"])

@pytest.mark.parametrize("payload", [
    {"display_name": "new_display_name"},
    {"email": "new_email@example.com"},
    {"display_name": "new_display_name", "email": "new_email@example.com"},
])

async def test_사용자가_변경하는_항목만_변경되고_나머지는_기존_값을_유지한다(
    client_with_auth: TestClient,
    payload: dict,
    host_user: User,
):
    before_data = host_user.model_dump()

    response = client_with_auth.patch("/account/me", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    for keey, value in payload.items():
        assert data[key] == value
    
    for key in UPDATABLE_FIELDS - frozenset(payload.keys()):
        assert data[key] == before_data[key]

async def test_최소_하나_이상_항목을_변경해야_하며_그렇지_않으면_오류를_일으킨다(
    client_with_auth: TestClient
):
    response = client_with_auth.patch("/account/me", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

async def test_비밀번호_변경_시_해싱_처리한_비밀번호가_저장되어야_한다(
    client_with_auth: TestClient,
    host_user: User,
    db_session: AsyncSession,
):
    before_password = host_user.hashed_password
    payload = {
        "password": "new_password",
        "password_again": "new_password",
    }

    response = client_with_auth.patch("/account/@me", json=payload)
    assert response.status_code == status.HTTP_200_OK
    
    await db_session.refresh(host_user)
    assert host_user.hashed_password != before_password
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, func, Column, AutoString
from pydantic import EmailStr
from sqlalchemy import UniqueConstraint
from sqlalchemy_utc import UtcDateTime

class User(SQLModel, table=True):
    __table__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_email")
    )

    id: int = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=40, description="user account ID")
    email: EmailStr = Field(max_length=128, description="user email")
    display_name: str = Field(max_length=40, description="user display name")
    password: str = Field(max_length=128, description="user password")
    is_host: bool = Field(default=False, description="Whether the user is a host")
    created_at: datetime = Field(
        default=None, 
        nullable=False, 
        sa_type=UtcDateTime,
        sa_column_kwargs={
            "server_default": func.now(),
        })
    updated_at: datetime = Field(
        default=None, 
        nullable=False, 
        sa_type=UtcDateTime,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": lambda: datetime.now(timezone.utc)
        })
    oauth_accounts: list["OAuthAccount"] = Relationship(back_populates="user")

class OAuthAccount(SQLModel, table=True):
    __table__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_user_id",
            name="uq_provider_provider_account_id",
        ),
    )

    id: int = Field(default=None, primary_key=True)

    provider: str = Field(max_length=10, description="OAuth provider")
    provider_account_id: str = Field(max_length=128, description="OAuth provider account ID")

    user_id: int = Field(foreign_key="users.id")
    user: USer = Relationship(back_populates="oauth_accounts")

    created_at: AwareDateTime = Field(
        default=None, 
        nullable=False,
        sa_type=UtcDateTime,
        sa_column_kwargs={
            "server_default": func.now(),
        },
    )
    updated_at: AwareDateTime = Field(
        default=None,
        nullable=False,
        sa_type=UtcDateTime,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": lambda: datetime.now(timezone.utc)
        }
    )
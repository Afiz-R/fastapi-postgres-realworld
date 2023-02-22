from typing import Optional

from pydantic import SecretStr

from schemas.base import BaseSchema


class LoginUser(BaseSchema):
    email: str
    password: SecretStr


class NewUser(BaseSchema):
    username: str
    email: str
    password: str


class User(BaseSchema):
    email: str
    token: str
    username: str
    bio: str | None
    image: str | None


class UserResponse(BaseSchema):
    user: User


class UpdateUser(BaseSchema):
    email: str | None = None
    token: str | None = None
    username: str | None = None
    bio: str | None = None
    image: str | None = None


class Profile(BaseSchema):
    username: str
    bio: str | None
    image: str | None
    following: bool = False


class ProfileResponse(BaseSchema):
    profile: Profile

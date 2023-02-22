from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from jose import JWTError, jwt
from odmantic import AIOEngine
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from starlette.requests import Request

from core.exceptions import CredentialsException, NotAuthenticatedException
from models.user import UserModel
from schemas.user import User
from settings import SETTINGS, EngineD


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenContent(BaseModel):
    username: str


PWD_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')


class OAuth2PasswordToken(OAuth2):
    def __init__(
        self,
        token_url: str,
        scheme_name: str | None = None,
        scopes: dict | None = None,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={'tokenUrl': token_url, 'scopes': scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=False)

    async def __call__(self, request: Request) -> str | None:
        authorization: str = request.headers.get('Authorization')  # type: ignore
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != 'token':
            return None
        return str(param)


OAUTH2_SCHEME = OAuth2PasswordToken(token_url='/users')

app = FastAPI()


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password):
    return PWD_CONTEXT.hash(password)


async def get_user_instance(engine: AIOEngine, username: str | None = None, email: str | None = None) -> UserModel | None:
    """Get a user instance from its username"""
    if username is not None:
        query = UserModel.username == username
    elif email is not None:
        query = UserModel.email == email
    else:
        return None
    user = await engine.find_one(UserModel, query)
    return user


async def authenticate_user(engine: AIOEngine, email: str, password: str) -> UserModel | None:
    """Verify the User/Password pair against the DB content"""
    user = await get_user_instance(engine, email=email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(user: UserModel) -> str:
    token_content = TokenContent(username=user.username)
    expire = datetime.utcnow() + timedelta(minutes=SETTINGS.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {'exp': expire, 'sub': token_content.json()}
    encoded_jwt = jwt.encode(to_encode, SETTINGS.SECRET_KEY.get_secret_value(), algorithm=SETTINGS.ALGORITHM)
    return str(encoded_jwt)


async def get_current_user_instance(token: str | None = Depends(OAUTH2_SCHEME), engine: AIOEngine = EngineD) -> UserModel:
    """Decode the JWT and return the associated User"""
    if token is None:
        raise NotAuthenticatedException()
    try:
        payload = jwt.decode(
            token,
            SETTINGS.SECRET_KEY.get_secret_value(),
            algorithms=[SETTINGS.ALGORITHM],
        )
    except JWTError:
        raise CredentialsException()

    try:
        token_content = TokenContent.parse_raw(payload.get('sub'))
    except ValidationError:
        raise CredentialsException()

    user = await get_user_instance(engine, username=token_content.username)
    if user is None:
        raise CredentialsException()
    return user


async def get_current_user_optional_instance(token: str = Depends(OAUTH2_SCHEME), engine: AIOEngine = EngineD) -> UserModel | None:
    try:
        user = await get_current_user_instance(token, engine)
        return user
    except HTTPException:
        return None


async def get_current_user(
    user_instance: UserModel = Depends(get_current_user_instance),
    token: str = Depends(OAUTH2_SCHEME),
) -> User:
    return User(token=token, **user_instance.dict())

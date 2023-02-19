from typing import Optional, Tuple

from odmantic import Model
from odmantic.bson import ObjectId


class UserModel(Model):
    username: str
    email: str
    hashed_password: str
    bio: str | None = None
    image: str | None = None
    following_ids: tuple[ObjectId, ...] = ()

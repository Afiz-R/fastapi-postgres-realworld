from schemas.base import BaseSchema


class TagsResponse(BaseSchema):
    tags: list[str]

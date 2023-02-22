from typing import List, Tuple

from odmantic.bson import ObjectId
from odmantic.engine import AIOEngine

from core.exceptions import (
    ArticleNotFoundException,
    CommentAuthorNotFoundException,
    CommentNotFoundException,
    NotCommentAuthorException,
)
from models.article import ArticleModel, CommentModel
from models.user import UserModel


def ensure_is_comment_author(user: UserModel, comment: CommentModel):
    if comment.author_id != user.id:
        raise NotCommentAuthorException()


async def add_new_comment(engine: AIOEngine, article: ArticleModel, comment: CommentModel):
    article.comments += (comment,)
    await engine.save(article)


async def get_article_comments_and_authors_by_slug(engine: AIOEngine, slug: str) -> list[tuple[CommentModel, UserModel]]:
    article = await engine.find_one(ArticleModel, ArticleModel.slug == slug)
    if article is None:
        raise ArticleNotFoundException()
    comment_authors = await engine.find(
        UserModel,
        UserModel.id.in_(comment.author_id for comment in article.comments),
    )
    try:
        return [
            (
                comment,
                next(user for user in comment_authors if user.id == comment.author_id),
            )
            for comment in article.comments
        ]

    except StopIteration:
        raise CommentAuthorNotFoundException()


def get_comment_and_index_from_id(article: ArticleModel, comment_id: ObjectId) -> tuple[CommentModel, int]:
    for index, comment in enumerate(article.comments):
        if comment.comment_id == comment_id:
            return comment, index
    raise CommentNotFoundException()


async def delete_comment_by_index(engine: AIOEngine, article: ArticleModel, index: int):
    article.comments = article.comments[:index] + article.comments[index + 1 :]
    await engine.save(article)

from sqlalchemy import (
    BINARY,
    TIMESTAMP,
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    sql,
)

metadata_obj = MetaData()

user_table = Table(
    'users',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('username', String(30)),
    Column('email', (String(30)), unique=True),
    Column('password_hash', String(30)),
    Column('bio', Text),
    Column('image', BINARY),
    Column('created_at', TIMESTAMP, default=sql.func.now()),
    Column('updated_at', TIMESTAMP, default=sql.func.now(), onupdate=sql.func.now()),
)

article_table = Table(
    'articles',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('slug', String(30), unique=True),
    Column('title', String(30)),
    Column('description', String(30)),
    Column('body', Text),
    Column('tag_list', String(30), ForeignKey('tags.name'), nullable=True),
    Column('created_at', TIMESTAMP, default=sql.func.now()),
    Column('updated_at', TIMESTAMP, default=sql.func.now(), onupdate=sql.func.now()),
    Column('author_id', Integer, ForeignKey('users.id')),
    Column('deleted_at', TIMESTAMP, nullable=True),
)

comment_table = Table(
    'comments',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('body', Text),
    Column('created_at', TIMESTAMP, default=sql.func.now()),
    Column('updated_at', TIMESTAMP, default=sql.func.now(), onupdate=sql.func.now()),
    Column('author_id', Integer, ForeignKey('users.id')),
    Column('article_id', Integer, ForeignKey('articles.id')),
    Column('deleted_at', TIMESTAMP, nullable=True),
)

favorite_table = Table(
    'favorites',
    metadata_obj,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('article_id', Integer, ForeignKey('articles.id'), primary_key=True),
)

follow_table = Table(
    'follows',
    metadata_obj,
    Column('created_at', TIMESTAMP, default=sql.func.now()),
    Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('followee_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('deleted_at', TIMESTAMP, nullable=True),
)

tags_table = Table(
    'tags',
    metadata_obj,
    Column('id', Integer, primary_key=True),
    Column('name', String(30), unique=True),
)

article_tag_table = Table(
    'article_tags',
    metadata_obj,
    Column('article_id', Integer, ForeignKey('articles.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True),
)

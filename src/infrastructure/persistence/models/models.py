from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    ForeignKey,
    Table,
    DateTime,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


post_tags_table = Table(
    "post_tags",
    Base.metadata,
    mapped_column("post_id", ForeignKey("posts.id"), primary_key=True),
    mapped_column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[List["User"]] = relationship(back_populates="role")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    role: Mapped["Role"] = relationship(back_populates="users")
    social_accounts: Mapped[List["SocialAccount"]] = relationship(back_populates="user")
    posts: Mapped[List["Post"]] = relationship(back_populates="author")
    approvals_given: Mapped[List["Approval"]] = relationship(back_populates="manager")


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    account_name: Mapped[Optional[str]] = mapped_column(String(150))
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    user: Mapped["User"] = relationship(back_populates="social_accounts")
    publications: Mapped[List["Publication"]] = relationship(back_populates="social_account")

    @property
    def is_token_expired(self) -> bool:
        return self.expires_at is not None and self.expires_at <= datetime.utcnow()


class PostType(Base):
    __tablename__ = "post_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    posts: Mapped[List["Post"]] = relationship(back_populates="post_type")


class PostStatus(Base):
    __tablename__ = "post_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    posts: Mapped[List["Post"]] = relationship(back_populates="status")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    content: Mapped[Optional[str]] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_type_id: Mapped[Optional[int]] = mapped_column(ForeignKey("post_types.id"))
    status_id: Mapped[int] = mapped_column(ForeignKey("post_statuses.id"), nullable=False)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )

    author: Mapped["User"] = relationship(back_populates="posts")
    post_type: Mapped[Optional["PostType"]] = relationship(back_populates="posts")
    status: Mapped["PostStatus"] = relationship(back_populates="posts")
    media_items: Mapped[List["Media"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan"
    )
    tags: Mapped[List["Tag"]] = relationship(
        secondary=post_tags_table,
        back_populates="posts"
    )
    publications: Mapped[List["Publication"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan"
    )
    approvals: Mapped[List["Approval"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan"
    )

    def schedule(self, when: datetime) -> None:
        self.scheduled_at = when

    def add_tag(self, tag: "Tag") -> None:
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: "Tag") -> None:
        if tag in self.tags:
            self.tags.remove(tag)

    @property
    def is_scheduled(self) -> bool:
        return self.scheduled_at is not None

    @property
    def is_ready_for_publication(self) -> bool:
        return self.scheduled_at is not None and len(self.approvals) > 0


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    post: Mapped["Post"] = relationship(back_populates="media_items")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    posts: Mapped[List["Post"]] = relationship(
        secondary=post_tags_table,
        back_populates="tags"
    )


class Publication(Base):
    __tablename__ = "publications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    social_account_id: Mapped[int] = mapped_column(
        ForeignKey("social_accounts.id"),
        nullable=False
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    response: Mapped[Optional[str]] = mapped_column(Text)

    post: Mapped["Post"] = relationship(back_populates="publications")
    social_account: Mapped["SocialAccount"] = relationship(back_populates="publications")

    def mark_published(self, published_at: Optional[datetime] = None) -> None:
        self.published_at = published_at or datetime.utcnow()
        self.status = "published"

    def mark_failed(self, response: str) -> None:
        self.status = "failed"
        self.response = response


class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    manager_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.current_timestamp()
    )

    post: Mapped["Post"] = relationship(back_populates="approvals")
    manager: Mapped["User"] = relationship(back_populates="approvals_given")
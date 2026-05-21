import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey,
    Index, Integer, JSON, String, Text, UniqueConstraint, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── 1. users ────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("provider", "provider_id"),)

    id:          Mapped[str]      = mapped_column(String(12),  primary_key=True)
    name:        Mapped[str]      = mapped_column(String(100), nullable=False)
    email:       Mapped[str]      = mapped_column(String(255), nullable=False, unique=True)
    provider:    Mapped[str]      = mapped_column(String(20),  nullable=False)  # 'google' | 'discord' | 'facebook' | 'line'
    provider_id: Mapped[str]      = mapped_column(String(255), nullable=False)
    role:        Mapped[str]      = mapped_column(String(10),  default="user")
    has_topics:  Mapped[bool]     = mapped_column(Boolean,     default=False)
    created_at:  Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at:  Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    notification_pref: Mapped[Optional["UserNotificationPref"]] = relationship(back_populates="user", uselist=False)
    preference:        Mapped[Optional["Preference"]]            = relationship(back_populates="user", uselist=False)
    comments:          Mapped[list["Comment"]]                   = relationship(back_populates="user")
    notifications:     Mapped[list["Notification"]]              = relationship(back_populates="user")
    collections:       Mapped[list["Collection"]]                = relationship(back_populates="user")


# ── 2. user_notification_prefs ───────────────────────────────────────────────

class UserNotificationPref(Base):
    __tablename__ = "user_notification_prefs"

    id:               Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:          Mapped[str]           = mapped_column(String(12), ForeignKey("users.id"), unique=True, nullable=False)
    # 各管道開關（預設只開 email）
    notify_email:     Mapped[bool]          = mapped_column(Boolean, default=True)
    notify_discord:   Mapped[bool]          = mapped_column(Boolean, default=False)
    notify_messenger: Mapped[bool]          = mapped_column(Boolean, default=False)
    notify_line:      Mapped[bool]          = mapped_column(Boolean, default=False)
    # 各管道的目標 ID（對應管道開啟後才需填入）
    email_address:    Mapped[Optional[str]] = mapped_column(String(255))   # 可覆寫 users.email
    discord_user_id:  Mapped[Optional[str]] = mapped_column(String(100))   # Discord 用戶 ID（用於 Bot DM）
    messenger_psid:   Mapped[Optional[str]] = mapped_column(String(100))   # Facebook Messenger PSID
    line_user_id:     Mapped[Optional[str]] = mapped_column(String(100))   # LINE 用戶 ID
    created_at:       Mapped[datetime]      = mapped_column(DateTime, default=_now)
    updated_at:       Mapped[datetime]      = mapped_column(DateTime, default=_now, onupdate=_now)

    user: Mapped["User"] = relationship(back_populates="notification_pref")


# ── 3. preferences ───────────────────────────────────────────────────────────

class Preference(Base):
    __tablename__ = "preferences"

    id:         Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id:    Mapped[str]      = mapped_column(String(12), ForeignKey("users.id"), unique=True, nullable=False)
    tags:       Mapped[dict]     = mapped_column(JSON, nullable=False)  # ["大型語言模型", ...]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now, onupdate=_now)

    user: Mapped["User"] = relationship(back_populates="preference")


# ── 4. news_articles ─────────────────────────────────────────────────────────

class NewsArticle(Base):
    __tablename__ = "news_articles"
    __table_args__ = (
        Index("idx_news_cached_until", "cached_until"),
        Index("idx_news_link_valid",   "link_valid"),
        Index("idx_news_published_at", text("published_at DESC")),
    )

    article_id:   Mapped[str]           = mapped_column(String(36), primary_key=True, default=_uuid)
    source_url:   Mapped[str]           = mapped_column(String(2048), nullable=False, unique=True)
    title:        Mapped[str]           = mapped_column(String(500),  nullable=False)
    content:      Mapped[Optional[str]] = mapped_column(Text)
    summary:      Mapped[Optional[str]] = mapped_column(Text)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    fetched_at:   Mapped[datetime]      = mapped_column(DateTime, nullable=False)
    cached_until: Mapped[datetime]      = mapped_column(DateTime, nullable=False)
    link_valid:   Mapped[bool]          = mapped_column(Boolean, default=True)
    categories:   Mapped[Optional[dict]] = mapped_column(JSON)         # ["語言模型", ...]
    created_at:   Mapped[datetime]      = mapped_column(DateTime, default=_now)
    updated_at:   Mapped[datetime]      = mapped_column(DateTime, default=_now, onupdate=_now)

    article_summary: Mapped[Optional["ArticleSummary"]] = relationship(back_populates="article", uselist=False)
    audio_cache:     Mapped[Optional["AudioCache"]]     = relationship(back_populates="article", uselist=False)
    comments:        Mapped[list["Comment"]]             = relationship(back_populates="article")
    collections:     Mapped[list["Collection"]]          = relationship(back_populates="article")


# ── 5. article_summaries ─────────────────────────────────────────────────────

class ArticleSummary(Base):
    __tablename__ = "article_summaries"
    __table_args__ = (
        Index("idx_summary_cached_until", "cached_until"),
    )

    summary_id:         Mapped[str]           = mapped_column(String(36), primary_key=True, default=_uuid)
    article_id:         Mapped[str]           = mapped_column(String(36), ForeignKey("news_articles.article_id"), unique=True, nullable=False)
    summary_content:    Mapped[str]           = mapped_column(Text, nullable=False)
    word_count:         Mapped[Optional[int]] = mapped_column(Integer)
    llm_model:          Mapped[Optional[str]] = mapped_column(String(50))
    generation_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    cached_until:       Mapped[datetime]      = mapped_column(DateTime, nullable=False)
    created_at:         Mapped[datetime]      = mapped_column(DateTime, default=_now)
    updated_at:         Mapped[datetime]      = mapped_column(DateTime, default=_now, onupdate=_now)

    article: Mapped["NewsArticle"] = relationship(back_populates="article_summary")


# ── 6. audio_caches ──────────────────────────────────────────────────────────

class AudioCache(Base):
    __tablename__ = "audio_caches"
    __table_args__ = (
        Index("idx_audio_article_id",   "article_id"),
        Index("idx_audio_cached_until", "cached_until"),
    )

    audio_id:         Mapped[str]           = mapped_column(String(36), primary_key=True, default=_uuid)
    article_id:       Mapped[str]           = mapped_column(String(36), ForeignKey("news_articles.article_id"), unique=True, nullable=False)
    file_url:         Mapped[str]           = mapped_column(String(1024), nullable=False)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    tts_engine:       Mapped[Optional[str]] = mapped_column(String(50))
    file_size_bytes:  Mapped[Optional[int]] = mapped_column(Integer)
    cached_until:     Mapped[datetime]      = mapped_column(DateTime, nullable=False)
    created_at:       Mapped[datetime]      = mapped_column(DateTime, default=_now)

    article: Mapped["NewsArticle"] = relationship(back_populates="audio_cache")


# ── 7. comments ──────────────────────────────────────────────────────────────

class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (
        Index("idx_comments_article_id", "article_id"),
        Index("idx_comments_parent_id",  "parent_comment_id"),
        Index("idx_comments_user_id",    "user_id"),
    )

    comment_id:        Mapped[str]            = mapped_column(String(36), primary_key=True, default=_uuid)
    article_id:        Mapped[str]            = mapped_column(String(36), ForeignKey("news_articles.article_id"), nullable=False)
    user_id:           Mapped[str]            = mapped_column(String(12), ForeignKey("users.id"), nullable=False)
    parent_comment_id: Mapped[Optional[str]]  = mapped_column(String(36), ForeignKey("comments.comment_id"))
    content:           Mapped[str]            = mapped_column(Text, nullable=False)
    is_moderated:      Mapped[bool]           = mapped_column(Boolean, default=False)
    moderation_score:  Mapped[Optional[float]] = mapped_column(Float)
    created_at:        Mapped[datetime]       = mapped_column(DateTime, default=_now)
    updated_at:        Mapped[datetime]       = mapped_column(DateTime, default=_now, onupdate=_now)

    article:  Mapped["NewsArticle"]    = relationship(back_populates="comments")
    user:     Mapped["User"]           = relationship(back_populates="comments")
    replies:  Mapped[list["Comment"]]  = relationship(back_populates="parent", foreign_keys=[parent_comment_id])
    parent:   Mapped[Optional["Comment"]] = relationship(back_populates="replies", remote_side=[comment_id])


# ── 8. notifications ─────────────────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("idx_notifications_user_id", "user_id"),
        Index("idx_notifications_status",  "status"),
    )

    notification_id: Mapped[str]           = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id:         Mapped[str]           = mapped_column(String(12), ForeignKey("users.id"), nullable=False)
    type:            Mapped[str]           = mapped_column(String(20), nullable=False)   # 'reply' | 'summary_done' | 'bookmark_remind'
    channel:         Mapped[str]           = mapped_column(String(15), nullable=False)   # 'email' | 'discord' | 'messenger' | 'line'
    title:           Mapped[Optional[str]] = mapped_column(String(255))
    content:         Mapped[Optional[str]] = mapped_column(Text)
    status:          Mapped[str]           = mapped_column(String(10), default="pending")  # 'pending' | 'sent' | 'failed'
    retry_count:     Mapped[int]           = mapped_column(Integer, default=0)
    sent_at:         Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at:      Mapped[datetime]      = mapped_column(DateTime, default=_now)

    user: Mapped["User"] = relationship(back_populates="notifications")


# ── 9. collections ───────────────────────────────────────────────────────────

class Collection(Base):
    __tablename__ = "collections"
    __table_args__ = (
        UniqueConstraint("user_id", "article_id"),
        Index("idx_collections_user_id",         "user_id"),
        Index("idx_collections_collection_date", "collection_date"),
    )

    collection_id:   Mapped[str]           = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id:         Mapped[str]           = mapped_column(String(12), ForeignKey("users.id"), nullable=False)
    article_id:      Mapped[str]           = mapped_column(String(36), ForeignKey("news_articles.article_id"), nullable=False)
    ai_summary:      Mapped[Optional[str]] = mapped_column(Text)
    keywords:        Mapped[Optional[dict]] = mapped_column(JSON)          # ["Transformer", ...]
    vector_id:       Mapped[Optional[str]] = mapped_column(String(100))    # 對應 ChromaDB 的向量 ID
    collection_date: Mapped[datetime]      = mapped_column(DateTime, default=_now)

    user:    Mapped["User"]        = relationship(back_populates="collections")
    article: Mapped["NewsArticle"] = relationship(back_populates="collections")

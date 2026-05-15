# src/api/v1/routers/posts.py
from datetime import datetime
from typing import Optional, Literal

from fastapi import APIRouter, Depends, Query

from src.api.v1.schemas.post import PostListResponse
from src.api.v1.dependencies import get_post_service
from src.core.dependencies import get_current_user
from src.infrastructure.persistence.repositories.post_repository import PostFilters
from src.modules.posts.service import PostService

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=PostListResponse, summary="Получить список постов")
def get_posts(
    # ── Пагинация ─────────────────────────────────────────────
    page:      int = Query(1,  ge=1,   description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Постов на странице"),

    # ── Фильтры ───────────────────────────────────────────────
    status_id:      Optional[int]           = Query(None, description="ID статуса поста"),
    post_type_id:   Optional[int]           = Query(None, description="ID типа поста"),
    author_id:      Optional[int]           = Query(None, description="ID автора"),
    tag_ids:        Optional[list[int]]     = Query(None, description="ID меток (AND-логика)"),
    scheduled_from: Optional[datetime]      = Query(None, description="Дата публикации от"),
    scheduled_to:   Optional[datetime]      = Query(None, description="Дата публикации до"),
    created_from:   Optional[datetime]      = Query(None, description="Дата создания от"),
    created_to:     Optional[datetime]      = Query(None, description="Дата создания до"),
    search:         Optional[str]           = Query(None, description="Поиск по заголовку и тексту"),

    # ── Сортировка ────────────────────────────────────────────
    order_by:  Literal["created_at", "updated_at", "scheduled_at", "title", "status_id"] = Query(
        "created_at", description="Поле сортировки"
    ),
    order_dir: Literal["asc", "desc"] = Query("desc", description="Направление"),

    # ── Зависимости ───────────────────────────────────────────
    service:      PostService = Depends(get_post_service),
    current_user                  = Depends(get_current_user),
):
    filters = PostFilters(
        status_id=status_id,
        post_type_id=post_type_id,
        author_id=author_id,
        tag_ids=tag_ids or [],
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
        created_from=created_from,
        created_to=created_to,
        search=search,
    )

    posts, total = service.get_posts(
        filters=filters,
        order_by=order_by,
        order_dir=order_dir,
        page=page,
        page_size=page_size,
        current_user=current_user,
    )

    return PostListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=posts,
    )
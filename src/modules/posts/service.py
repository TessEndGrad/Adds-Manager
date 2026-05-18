from src.infrastructure.persistence.repositories.post_repository import (
    PostRepository,
    PostFilters,
)
from src.infrastructure.persistence.models.post import Post


class PostService:
    def __init__(self, repository: PostRepository) -> None:
        self._repo = repository

    def get_posts(
        self,
        filters: PostFilters,
        order_by: str,
        order_dir: str,
        page: int,
        page_size: int,
        current_user,
    ) -> tuple[list[Post], int]:
        """
        Бизнес-правила видимости постов:
        - Обычный пользователь (role_id != 1) видит только свои посты
        - Менеджер/админ (role_id == 1) видит все посты
        """
        if current_user.role_id != 1:
            filters.author_id = current_user.id

        return self._repo.get_list(
            filters=filters,
            order_by=order_by,
            order_dir=order_dir,
            page=page,
            page_size=page_size,
        )
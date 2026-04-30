from typing import List, Optional

import strawberry
from django.contrib.auth import get_user_model
from strawberry_django import field as dj_field
from strawberry_django import mutations

from . import inputs, models, permissions, types

User = get_user_model()


@strawberry.type
class Query:
    categories: List[types.CategoryType] = dj_field(
        filters=types.CategoryFilter, pagination=True
    )
    posts: List[types.PostType] = dj_field(filters=types.PostFilter, pagination=True)

    @strawberry.field
    async def category_by_slug(self, slug: str) -> Optional[types.CategoryType]:
        return await models.Category.objects.filter(
            slug=slug,
            is_active=True,
        ).afirst()

    @strawberry.field
    async def post_by_slug(self, slug: str) -> Optional[types.PostType]:
        return await models.Post.objects.filter(
            title_slug=slug,
            status=models.Post.Status.PUBLISHED,
            is_active=True,
        ).afirst()


@strawberry.type
class Mutation:
    # Strawberry-Django mutations handle the async context automatically
    # when the schema is executed asynchronously.
    create_category: types.CategoryType = mutations.create(
        inputs.CategoryInput,
        permission_classes=[permissions.IsStaff],
        handle_django_errors=True,  # You get your clean Error Union!
    )
    create_post: types.PostType = mutations.create(
        inputs.PostInput,
        permission_classes=[permissions.IsAuthenticated],
        handle_django_errors=True,  # You get your clean Error Union!
    )
    update_post: types.PostType = mutations.update(
        inputs.PostUpdateInput,
        permission_classes=[
            permissions.IsAuthenticated,
            (permissions.IsOwnerGuard(models.Post) or permissions.IsSuperuser),
        ],
        handle_django_errors=True,  # You get your clean Error Union!
    )

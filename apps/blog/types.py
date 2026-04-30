from typing import List, Optional

import strawberry
from django.contrib.auth import get_user_model
from strawberry_django import filter_type as dj_filter_type
from strawberry_django import type as dj_type

from . import models

User = get_user_model()


@dj_type(models.Category)
class CategoryType:
    id: strawberry.auto
    name: strawberry.auto
    slug: strawberry.auto
    posts: List["PostType"]
    created_at: strawberry.auto
    updated_at: strawberry.auto
    created_by: Optional["UserType"]
    updated_by: Optional["UserType"]

    @classmethod
    def get_queryset(cls, queryset, info, **kwargs):
        return queryset.filter(is_active=True)


@dj_type(models.Post)
class PostType:
    id: strawberry.auto
    title: strawberry.auto
    title_slug: strawberry.auto
    category: Optional[CategoryType]
    body: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto
    created_by: Optional["UserType"]
    updated_by: Optional["UserType"]

    @classmethod
    def get_queryset(cls, queryset, info, **kwargs):
        return queryset.filter(
            is_active=True,
            status=models.Post.Status.PUBLISHED,
        )


@dj_type(User)
class UserType:
    username: strawberry.auto
    first_name: strawberry.auto
    last_name: strawberry.auto

    @strawberry.field
    def full_name(self) -> str:
        return self.get_full_name()


@dj_filter_type(models.Post, lookups=True)
class PostFilter:
    id: strawberry.auto
    title: strawberry.auto
    title_slug: strawberry.auto
    category: Optional["CategoryFilter"]


@dj_filter_type(models.Category, lookups=True)
class CategoryFilter:
    id: strawberry.auto
    name: strawberry.auto
    slug: strawberry.auto

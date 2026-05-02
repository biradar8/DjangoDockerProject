from typing import List, Optional

import strawberry
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.timesince import timesince
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
    status: models.Post.Status
    category: Optional[CategoryType]
    body: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto
    created_by: Optional["UserType"]
    updated_by: Optional["UserType"]

    @strawberry.field
    def read_created_at(self) -> Optional[str]:
        if not self.created_at:
            return None
        time_ago = timesince(self.created_at).split(",")[0] + " ago"
        formatted = self.created_at.strftime("%b %d, %Y • %I:%M %p")
        return f"{formatted} • {time_ago}"

    @classmethod
    def get_queryset(cls, queryset, info, **kwargs):
        request = info.context.get("request")
        base_qs = queryset.filter(is_active=True)
        if request and request.user.is_authenticated:
            return base_qs.filter(
                Q(status=models.Post.Status.PUBLISHED) | Q(created_by=request.user)
            )
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
    status: Optional[models.Post.Status]
    created_at: strawberry.auto
    created_by: Optional["UserFilter"]


@dj_filter_type(User, lookups=True)
class UserFilter:
    username: strawberry.auto


@dj_filter_type(models.Category, lookups=True)
class CategoryFilter:
    id: strawberry.auto
    name: strawberry.auto
    slug: strawberry.auto

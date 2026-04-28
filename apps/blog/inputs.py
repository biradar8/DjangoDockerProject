import strawberry
from strawberry_django import input as dj_input

from . import models


@dj_input(models.Category)
class CategoryInput:
    name: strawberry.auto


@dj_input(models.Post)
class PostInput:
    title: strawberry.auto
    body: strawberry.auto
    status: strawberry.auto
    category: strawberry.auto
    is_active: strawberry.auto


@dj_input(models.Post, partial=True)
class PostUpdateInput:
    id: strawberry.auto
    title: strawberry.auto
    body: strawberry.auto
    status: strawberry.auto
    category: strawberry.auto
    is_active: strawberry.auto

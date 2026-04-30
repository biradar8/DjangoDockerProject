import pytest
from blog.models import Category, Post
from django.contrib.auth import get_user_model

from config.schema import schema

pytestmark = pytest.mark.django_db(transaction=True, databases="__all__")
User = get_user_model()


async def test_query_categories(mock_context):
    # Setup
    user = await User.objects.acreate(username="testuser")
    await Category.objects.acreate(name="Category 1", slug="category-1")
    await Category.objects.acreate(name="Category 2", slug="category-2")

    context = mock_context(user)

    query = """
        query {
          categories {
            id
            name
            slug
          }
        }
    """

    result = await schema.execute(query, context_value=context)

    assert result.errors is None
    assert len(result.data["categories"]) == 2
    names = [c["name"] for c in result.data["categories"]]
    assert "Category 1" in names
    assert "Category 2" in names


async def test_query_posts(mock_context):
    # Setup
    user = await User.objects.acreate(username="testuser")
    cat = await Category.objects.acreate(name="Cat 1", slug="cat-1")
    await Post.objects.acreate(
        title="Post 1",
        title_slug="post-1",
        body="Body 1",
        category=cat,
        status=Post.Status.PUBLISHED,
    )
    await Post.objects.acreate(
        title="Post 2",
        title_slug="post-2",
        body="Body 2",
        category=cat,
        status=Post.Status.PUBLISHED,
    )

    context = mock_context(user)

    query = """
        query {
          posts {
            id
            title
            titleSlug
          }
        }
    """

    result = await schema.execute(query, context_value=context)

    assert result.errors is None
    assert len(result.data["posts"]) == 2
    titles = [p["title"] for p in result.data["posts"]]
    assert "Post 1" in titles
    assert "Post 2" in titles


async def test_query_category_by_slug(mock_context):
    # Setup
    user = await User.objects.acreate(username="testuser")
    await Category.objects.acreate(
        name="Specific Category", slug="specific-cat", is_active=True
    )

    context = mock_context(user)

    query = """
        query GetCat($slug: String!) {
          categoryBySlug(slug: $slug) {
            id
            name
          }
        }
    """

    result = await schema.execute(
        query, context_value=context, variable_values={"slug": "specific-cat"}
    )

    assert result.errors is None
    assert result.data["categoryBySlug"]["name"] == "Specific Category"


async def test_query_post_by_slug(mock_context):
    # Setup
    user = await User.objects.acreate(username="testuser")
    cat = await Category.objects.acreate(name="Cat", slug="cat")
    await Post.objects.acreate(
        title="Specific Post",
        title_slug="specific-post",
        body="Body",
        category=cat,
        is_active=True,
        status=Post.Status.PUBLISHED,
    )

    context = mock_context(user)

    query = """
        query GetPost($slug: String!) {
          postBySlug(slug: $slug) {
            id
            title
            titleSlug
          }
        }
    """

    result = await schema.execute(
        query, context_value=context, variable_values={"slug": "specific-post"}
    )

    assert result.errors is None
    assert result.data["postBySlug"]["title"] == "Specific Post"

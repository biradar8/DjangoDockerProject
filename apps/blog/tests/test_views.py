import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.text import slugify

from blog.models import Category, Post

User = get_user_model()

pytestmark = pytest.mark.django_db(transaction=True, databases="__all__")


@pytest.fixture
def test_data():
    # 1. Create a test user
    user = User.objects.create_user(username="testuser", password="password")

    # 2. Create test categories
    cat_tech = Category.objects.create(name="Tech", slug="tech")
    cat_news = Category.objects.create(name="News", slug="news")

    # 3. Create test posts assigned to categories
    Post.objects.create(
        title="GraphQL Tutorial",
        title_slug=slugify("GraphQL Tutorial"),
        body="Learning GraphQL with Strawberry.",
        created_by=user,
        category=cat_tech,
        status=Post.Status.PUBLISHED,
    )
    Post.objects.create(
        title="Django Updates",
        title_slug=slugify("Django Updates"),
        body="What is new in Django.",
        created_by=user,
        category=cat_tech,
        status=Post.Status.PUBLISHED,
    )
    Post.objects.create(
        title="World News",
        title_slug=slugify("World News"),
        body="Global happenings today.",
        created_by=user,
        category=cat_news,
        status=Post.Status.PUBLISHED,
    )


def test_index_view_loads_all_posts(client, test_data):
    """Test that the index view loads and returns all posts by default."""
    response = client.get(reverse("blog:index"))
    assert response.status_code == 200
    assert len(response.context["posts"]) == 3


def test_index_view_search_filter(client, test_data):
    """Test the text search query parameter (?q=...)."""
    response = client.get(reverse("blog:index"), {"q": "GraphQL"})
    assert response.status_code == 200
    assert len(response.context["posts"]) == 1
    assert response.context["posts"][0]["title"] == "GraphQL Tutorial"
    assert response.context["search_term"] == "GraphQL"


def test_index_view_category_filter(client, test_data):
    """Test the category filter query parameter (?category=...)."""
    response = client.get(reverse("blog:index"), {"category": "tech"})
    assert response.status_code == 200
    assert len(response.context["posts"]) == 2

    # Ensure 'World News' (which is in the 'news' category) is not included
    returned_titles = [p["title"] for p in response.context["posts"]]
    assert "GraphQL Tutorial" in returned_titles
    assert "Django Updates" in returned_titles
    assert "World News" not in returned_titles
    assert response.context["selected_category"] == "tech"


def test_index_view_search_and_category_combined(client, test_data):
    """Test combining both search and category parameters."""
    response = client.get(reverse("blog:index"), {"q": "Django", "category": "tech"})
    assert response.status_code == 200
    assert len(response.context["posts"]) == 1
    assert response.context["posts"][0]["title"] == "Django Updates"

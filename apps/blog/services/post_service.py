from asgiref.sync import async_to_sync
from django.http import Http404

from config.schema import schema

GET_POSTS_QUERY = """
query GetAllPosts(
  $limit: Int = 10
  $offset: Int = 0
  $search: String
  $categorySlug: String
) {
  posts(
    pagination: { limit: $limit, offset: $offset }
    filters: {
      title: { iContains: $search }
      category: { slug: { exact: $categorySlug } }
    }
  ) {
    id
    title
    titleSlug
    body
    readCreatedAt
    createdBy {
      username
    }
    category {
      name
    }
  }
}
"""

GET_POST_BY_SLUG_QUERY = """
query GetPost($slug: String!) {
  postBySlug(slug: $slug) {
    id
    title
    body
    readCreatedAt
    createdBy {
      username
    }
    category {
      name
    }
  }
}
"""


def fetch_posts(request, limit=10, offset=0, search="", category_slug: str = None):
    variables = {
        "limit": limit,
        "offset": offset,
        "search": search,
        "categorySlug": category_slug,
    }

    result = async_to_sync(schema.execute)(
        GET_POSTS_QUERY,
        variable_values=variables,
        context_value={"request": request},
    )

    if result.errors:
        return []

    return result.data.get("posts", [])


def fetch_post_by_slug(request, slug: str):
    result = async_to_sync(schema.execute)(
        GET_POST_BY_SLUG_QUERY,
        variable_values={"slug": slug},
        context_value={"request": request},
    )

    if result.errors:
        # You can log errors here
        raise Http404("Post not found.")

    post = result.data.get("postBySlug") if result.data else None

    if not post:
        raise Http404("Post not found.")

    return post

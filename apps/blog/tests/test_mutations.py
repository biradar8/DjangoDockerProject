import pytest
from blog.models import Category, Post
from django.contrib.auth import get_user_model

from config.schema import schema

pytestmark = pytest.mark.django_db(transaction=True, databases="__all__")
User = get_user_model()


async def test_create_post_success(mock_context):
    # 1. Setup: Create user and category
    user = await User.objects.acreate(username="testadmin", email="admin@test.com")

    # 2. acreate() instantly populates cat.id! No refresh needed.
    cat = await Category.objects.acreate(name="Test Category")

    assert cat.id is not None, "Django failed to generate a Primary Key!"

    context = mock_context(user)

    # 3. The Query: Inject the ID directly
    mutation = """
            mutation CreateTestPost($categoryId: ID!) {
              createPost(
                data: {
                    title: "My Async Test", 
                    body: "This is a test.", 
                    category: {set: $categoryId} 
                }
              ) {
                ... on PostType {
                  id
                  title
                  titleSlug
                }
                ... on OperationInfo {
                  messages {
                    field
                    message
                  }
                }
              }
            }
        """

    # 4. Execute the mutation directly against the Python schema
    result = await schema.execute(
        mutation,
        context_value=context,
        variable_values={"categoryId": cat.id},
    )

    # 5. Assertions: Prove it worked!
    assert result.errors is None  # No catastrophic GraphQL errors

    # Extract the payload
    post_data = result.data["createPost"]

    # Prove the post was created and the title matches
    assert post_data["title"] == "My Async Test"
    # Prove our custom slug logic fired
    assert post_data["titleSlug"] == "my-async-test"


# @pytest.mark.django_db(transaction=True)
async def test_update_post_blocks_non_owners(mock_context):
    # 1. Setup: Create TWO users
    owner = await User.objects.acreate(username="owner")
    hacker = await User.objects.acreate(username="hacker")

    # 2. Setup: Create a post owned by the 'owner'
    post = await Post.objects.acreate(
        title="Original Title", body="Original Body", created_by=owner
    )

    # 3. Setup: The 'hacker' is the one making the request!
    context = mock_context(hacker)

    # 4. The Query: Updated to match mutations.update() factory syntax
    mutation = """
        mutation MyMutation($id: ID = "") {
          updatePost(data: {id: $id, title: "Hacked Title"}) {
            ... on PostType {
              id
              title
            }
            ... on OperationInfo {
              __typename
              messages {
                message
                field
              }
            }
          }
        }
    """

    # 5. Execute
    result = await schema.execute(
        mutation,
        context_value=context,
        variable_values={"id": post.id},
    )

    # 6. Assertions: Prove it failed securely
    assert result.errors is not None
    assert len(result.errors) == 1

    # Prove the exact error message from our IsOwnerGuard fired
    error_message = str(result.errors[0])
    assert "You do not have permission" in error_message

    # Prove the database was NOT changed
    await post.arefresh_from_db(using="default")
    assert post.title == "Original Title"  # Still the original!


async def test_create_category_staff_only(mock_context):
    # Setup: Create normal user (not staff)
    user = await User.objects.acreate(username="normaluser", is_staff=False)
    context = mock_context(user)

    mutation = """
        mutation {
          createCategory(data: {name: "Staff Only Cat"}) {
            ... on CategoryType {
              id
              name
            }
            ... on OperationInfo {
              messages {
                message
                field
              }
            }
          }
        }
    """

    result = await schema.execute(mutation, context_value=context)

    assert result.errors is not None
    assert "You must be a staff member to perform this action." in str(result.errors[0])


async def test_create_category_success(mock_context):
    # Setup: Create staff user
    user = await User.objects.acreate(username="staffuser", is_staff=True)
    context = mock_context(user)

    mutation = """
        mutation {
          createCategory(data: {name: "Staff Only Cat"}) {
            ... on CategoryType {
              id
              name
              slug
            }
            ... on OperationInfo {
              messages {
                message
                field
              }
            }
          }
        }
    """

    result = await schema.execute(mutation, context_value=context)

    assert result.errors is None
    category_data = result.data["createCategory"]
    assert category_data["name"] == "Staff Only Cat"
    # Slug usually auto-generated if not provided, assuming it is here, but let's check basic creation

import strawberry
from django.contrib.auth import aauthenticate, alogin, alogout
from strawberry.types import Info

from blog.schema import Mutation as BlogQueryMutation  # type: ignore
from blog.schema import Query as BlogQuery  # type: ignore

from .graphql_extensions import ErrorLoggingExtension, MutationRoutingExtension


@strawberry.type
class LoginPayload:
    success: bool
    message: str
    username: str | None = None


@strawberry.type
class AuthMutation:
    @strawberry.mutation
    async def login(self, info: Info, username: str, password: str) -> LoginPayload:
        request = info.context.request

        # Authenticate the user asynchronously
        user = await aauthenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            # Log the user into the session
            await alogin(request, user)
            return LoginPayload(
                success=True,
                message="Login successful.",
                username=user.username,
            )

        return LoginPayload(
            success=False,
            message="Invalid credentials.",
        )

    @strawberry.mutation
    async def logout(self, info: Info) -> bool:
        request = info.context.request
        await alogout(request)
        return True


@strawberry.type
class Query(BlogQuery):
    pass


@strawberry.type
class Mutation(AuthMutation, BlogQueryMutation):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        ErrorLoggingExtension,
        MutationRoutingExtension,
    ],
)

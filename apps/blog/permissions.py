from typing import Any

from strawberry.permission import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):
    message = "You must be logged in to perform this action."

    async def has_permission(self, source: any, info: Info, **kwargs) -> bool:
        request = info.context.get("request")
        if not request or not request.user:
            return False
        return request.user.is_authenticated


class IsStaff(BasePermission):
    message = "You must be a staff member to perform this action."

    async def has_permission(self, source: any, info: Info, **kwargs) -> bool:
        request = info.context.get("request")
        if not request or not request.user:
            return False
        return request.user.is_authenticated and request.user.is_staff


class IsSuperuser(BasePermission):
    message = "You must be a superuser to perform this action."

    async def has_permission(self, source: any, info: Info, **kwargs) -> bool:
        request = info.context.get("request")
        if not request or not request.user:
            return False
        return request.user.is_authenticated and request.user.is_superuser


def IsOwnerGuard(model_class, arg_name="id"):
    """
    A factory that generates a Strawberry Permission class for any model.
    It expects the mutation to pass the object's ID via `arg_name`.
    """

    class _IsOwner(BasePermission):
        message = "You do not have permission to modify this object."

        async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
            user = info.context.request.user

            payload = kwargs.get("data")
            obj_id = getattr(payload, arg_name, None)
            if not obj_id:
                return False

            try:
                # OPTIMIZATION: .only() prevents fetching heavy text/data columns
                # We only need the database to return the owner's ID
                obj = await model_class.objects.only("created_by_id").aget(id=obj_id)

                # Compare the raw database integer to avoid triggering a related User query
                return obj.created_by_id == user.id

            except model_class.DoesNotExist:
                # Dynamically set the error message based on the model name!
                self.message = f"{model_class.__name__} not found."
                return False

    return _IsOwner

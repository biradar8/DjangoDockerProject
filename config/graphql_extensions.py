import logging

from strawberry.extensions import SchemaExtension

from .routers import pin_to_primary

logger = logging.getLogger(__name__)


class ErrorLoggingExtension(SchemaExtension):
    def on_operation(self):
        yield
        if self.execution_context.result and self.execution_context.result.errors:
            for error in self.execution_context.result.errors:
                logger.error(
                    f"GraphQL Error: {error.message}", exc_info=error.original_error
                )


class MutationRoutingExtension(SchemaExtension):
    """Pins all database reads to the primary if the operation is a mutation."""

    def on_operation(self):
        query_string = getattr(self.execution_context, "query", "") or ""
        is_mutation = "mutation" in query_string

        if is_mutation:
            # Pin the router to the primary for the duration of this request
            token = pin_to_primary.set(True)

        yield

        if is_mutation:
            # Unpin it safely when the request is over
            pin_to_primary.reset(token)

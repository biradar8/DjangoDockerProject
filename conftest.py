import pytest
from django.db import connections


@pytest.fixture
def mock_context():
    def _create_context(user):
        class MockRequest:
            def __init__(self, u):
                self.user = u

        class CustomContext:
            def __init__(self, u):
                self.request = MockRequest(u)

            def get(self, key, default=None):
                return getattr(self, key, default)

        return CustomContext(user)

    return _create_context


@pytest.fixture(autouse=True)
def close_db_connections_after_test():
    yield
    for conn in connections.all():
        conn.close()

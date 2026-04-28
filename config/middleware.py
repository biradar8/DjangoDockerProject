import contextvars
import threading
import time

from asgiref.sync import iscoroutinefunction
from django.db import connections
from django.db.utils import OperationalError
from django.utils.decorators import sync_and_async_middleware

from .db_health import set_replica_health

user_var = contextvars.ContextVar("user", default=None)


def get_current_user():
    return user_var.get()


_checker_started = False
_lock = threading.Lock()


def check_replica_loop():
    """Background thread that pings the replica every 10 seconds."""
    while True:
        try:
            # We use a low-level cursor to ping
            with connections["replica"].cursor() as cursor:
                cursor.execute("SELECT 1")
            set_replica_health(True)
        except OperationalError:
            set_replica_health(False)
        time.sleep(10)


@sync_and_async_middleware
def DatabaseHealthMiddleware(get_response):
    # 1. This outer block acts exactly like __init__ (runs once at startup)
    global _checker_started
    with _lock:
        if not _checker_started:
            thread = threading.Thread(target=check_replica_loop, daemon=True)
            thread.start()
            _checker_started = True

    # 2. Django passes the wrapped response. We define how to handle it.
    if iscoroutinefunction(get_response):

        async def middleware(request):
            return await get_response(request)
    else:

        def middleware(request):
            return get_response(request)

    return middleware


@sync_and_async_middleware
def GlobalUserMiddleware(get_response):
    # This outer block acts exactly like __init__
    if iscoroutinefunction(get_response):

        async def middleware(request):
            # ASYNC PATH
            user = await request.auser()
            request.user = user

            token = user_var.set(user)
            try:
                return await get_response(request)
            finally:
                user_var.reset(token)
    else:

        def middleware(request):
            # SYNC PATH
            user = getattr(request, "user", None)
            if user is not None and type(user).__name__ == "SimpleLazyObject":
                user._setup()
                user = user._wrapped
                request.user = user

            token = user_var.set(user)
            try:
                return get_response(request)
            finally:
                user_var.reset(token)

    return middleware

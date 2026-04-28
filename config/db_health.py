_replica_healthy = True


def is_replica_available():
    global _replica_healthy
    return _replica_healthy


def set_replica_health(status: bool):
    global _replica_healthy
    _replica_healthy = status

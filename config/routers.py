import contextvars

from .db_health import is_replica_available

# This variable acts as our "Sticky" switch
pin_to_primary = contextvars.ContextVar("pin_to_primary", default=False)


class PrimaryReplicaRouter:
    def db_for_read(self, model, **hints):

        # Manual overide, pin DB to the primary
        if pin_to_primary.get():
            return "default"

        if is_replica_available():
            return "replica"
        return "default"

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == "default"

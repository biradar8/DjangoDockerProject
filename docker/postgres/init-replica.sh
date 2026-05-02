#!/bin/sh
set -e

DATA_DIR="/var/lib/postgresql/data"
SUCCESS_FLAG="$DATA_DIR/.backup_complete"

# 1. Check if our custom success flag exists
if [ -f "$SUCCESS_FLAG" ] && [ -s "$DATA_DIR/PG_VERSION" ]; then
  echo "Valid data exists. Starting as existing replica..."
else
  echo "Data is missing or corrupted. Wiping and cloning from primary..."
  
  # 2. Wipe the directory clean in case there is half-finished corrupted data
  rm -rf $DATA_DIR/*
  # Remove hidden files if any exist, ignoring errors
  rm -rf $DATA_DIR/.* 2>/dev/null || true 
  # We use || true so the script doesn't crash if the slot was already deleted.
  echo "Cleaning up old replication slots on primary..."
  PGPASSWORD=${DB_PASSWORD} psql -h ${DB_PRIMARY_HOST} -U ${DB_USER} -d postgres -c "SELECT pg_drop_replication_slot('replica_slot_1');" || true

  # 3. Run the backup
  su-exec postgres pg_basebackup -h ${DB_PRIMARY_HOST} -D $DATA_DIR -U ${DB_USER} -P -R -X stream --create-slot --slot=replica_slot_1

  # 4. Fix permissions
  chown -R postgres:postgres $DATA_DIR
  chmod 700 $DATA_DIR

  # 5. THE FIX: Create the success flag ONLY after everything succeeded
  su-exec postgres touch "$SUCCESS_FLAG"

  echo "Replica backup complete. Starting server..."
fi

# 6. Start the server
exec su-exec postgres postgres -c config_file=/etc/postgresql/postgresql.conf
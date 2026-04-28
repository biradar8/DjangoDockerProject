#!/bin/sh
set -e

# 1. Wait for the primary to be ready
until pg_isready -h ${DB_PRIMARY_HOST} -p 5432 -U ${DB_USER}; do
  echo "Waiting for ${DB_PRIMARY_HOST} database..."
  sleep 2
done

# 2. Clear existing data
# We do this as root to ensure we can wipe the directory
rm -rf /var/lib/postgresql/data/*

# 3. Run the backup as the 'postgres' user
# This ensures all the new files are owned by the correct user
su-exec postgres pg_basebackup -h ${DB_PRIMARY_HOST} -D /var/lib/postgresql/data -U ${DB_USER} -P -R -X stream
chmod 700 /var/lib/postgresql/data

# 4. Start the server as the 'postgres' user
echo "Replica backup complete. Starting server..."
exec su-exec postgres postgres
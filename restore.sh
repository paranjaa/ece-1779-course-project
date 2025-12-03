#!/bin/bash

#set up variables first

RCLONE_REMOTE="gdrive"
LOCAL_BACKUP_DIR="/opt/db_backups"
DB_NAME=$(cat ~/.secrets/.db_name.txt)
DB_USER=$(cat ~/.secrets/.db_user.txt)


#Find the DB container to run the postgres commands on
DB_CONTAINER=$(docker ps --filter "name=ece1779-project_db" --format "{{.Names}}" | head -n 1)
if [[ -z "$DB_CONTAINER" ]]; then
  echo "error, couldn't find a running DB container with name: ece1779-project_db"
  echo "verify docker setup and droplet "
  exit 1
fi

echo "Using DB container: $DB_CONTAINER"

#get the latest backupfile from the remote directory
LATEST_BACKUP=$(rclone ls "$RCLONE_REMOTE:" --fast-list | awk '{print $2}' | sort | grep "${DB_NAME}_" | tail -n 1)
if [[ -z "$LATEST_BACKUP" ]]; then
  echo "error, couldn't find a backup file, like ${DB_NAME}_timestamp"
  echo "check remote directory and rclone config"
  exit 1
fi


echo "Found latest backup at $LATEST_BACKUP, downloading"

rclone copy "$RCLONE_REMOTE:$LATEST_BACKUP" "$LOCAL_BACKUP_DIR/"

LOCAL_FILE="$LOCAL_BACKUP_DIR/$(basename "$LATEST_BACKUP")"
echo "Downloaded to: ${LOCAL_FILE}"

gzip -df "${LOCAL_FILE}"

SQL_FILE="${LOCAL_FILE%.gz}"

echo "Decompressed to sql file: ${SQL_FILE}"

read -p "Can you confirm restoring that ^ backup file? It will erase and replace the current '${DB_NAME}' database. (yes/no): " confirm
if [[ "$confirm" != "yes" ]]; then
    echo "Cancelling restoration script, "
    exit 0
fi

echo "Confirmed, restoring database to that backup"

echo "Verifying DB connection again..."
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "\l" > /dev/null
echo "Connection OK"

echo "Dropping existing database: ${DB_NAME}"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};"

echo "Creating new database: ${DB_NAME}"
docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE ${DB_NAME};"

echo "Applying backup to database..."
docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" < "${SQL_FILE}"

echo "Database Restoration complete"

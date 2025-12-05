#!/bin/bash
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin

# get these from the .secret files, was hardcoded before
DB_NAME=$(cat /root/.secrets/.db_name.txt)
DB_USER=$(cat /root/.secrets/.db_user.txt)
DB_PASSWORD=$(cat /root/.secrets/.db_password.txt)

echo "Backup started at $(date)"
whoami
pwd



#echo "Backing up database"


echo "Checking docker container before backup"
#get the name of the container that's running postgres
CONTAINER=$(docker ps --filter "name=ece1779-project_db" --format "{{.Names}}" | head -n 1)

#container is empty, there's probably bigger problems
if [[ -z "$CONTAINER" ]]; then
  echo "ERROR: Could not find a running DB container with name containing 'ece1779-project_db'"
  exit 1
fi

echo "Found docker conainter at : ${CONTAINER}"

#this should match the name of the rclone remote setup
RCLONE_REMOTE="gdrive"
#since the remote directory is set in that config, keep this blank
REMOTE_DIR=""



LOCAL_BACKUP_DIR="/opt/db_backups"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE_NAME="${DB_NAME}_${DATE}.sql"
COMPRESSED_FILE="${BACKUP_FILE_NAME}.gz"


echo "Dumping SQL database at ${LOCAL_BACKUP_DIR}/${BACKUP_FILE_NAME}"
docker exec "$CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" > "${LOCAL_BACKUP_DIR}/${BACKUP_FILE_NAME}"

echo "Compressing Local Copy at ${LOCAL_BACKUP_DIR}:/${BACKUP_FILE_NAME}"
gzip "${LOCAL_BACKUP_DIR}/${BACKUP_FILE_NAME}"

#move  the copy to the remote directory
echo "Copying backup file to remote directory, at ${RCLONE_REMOTE}, ${REMOTE_DIR}"
rclone copy "${LOCAL_BACKUP_DIR}/${COMPRESSED_FILE}" "${RCLONE_REMOTE}:${REMOTE_DIR}"

#delete local backups that are older than 7 days
echo "Deleting week old backup files"
find "$LOCAL_BACKUP_DIR" -name "${DB_NAME}_*.gz" -type f -mtime +7 -delete

echo "Database backup complete"

#probably would need a deletion for remote files, not going to come up in this timeframe though
#rclone delete --min-age 30d "${RCLONE_REMOTE}:${REMOTE_DIR}"
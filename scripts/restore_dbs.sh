#!/bin/bash
set -e

# Configuration
CENTRAL_POSTGRES_CONTAINER="central-postgres"
DB_USER="admin"
DB_PASS="central_admin_password_2025"

# Paths
ISS_BACKUP="/home/autcir_gmail_com/develop/backup/iss/backups/2025/12/iss_20251220_153000.sql.gz.gpg"
SC_BACKUP="/home/autcir_gmail_com/develop/backup/studiocentos/backups/2025/12/studiocentos_20251220_153000.sql.gz.gpg"

# Check if backups exist
if [ ! -f "$ISS_BACKUP" ] || [ ! -f "$SC_BACKUP" ]; then
    echo "❌ Error: Backup files not found!"
    exit 1
fi

echo "🔐 Enter GPG Password to decrypt backups:"
read -s GPG_PASS
echo ""

# Function to restore a single database
restore_db() {
    local backup_file=$1
    local db_name=$2
    local temp_gz="${backup_file%.gpg}"
    
    echo "---------------------------------------------------"
    echo "🔄 Processing ${db_name}..."
    
    echo "🔓 Decrypting $(basename $backup_file)..."
    # Decrypt
    echo "$GPG_PASS" | gpg --batch --yes --passphrase-fd 0 --output "$temp_gz" --decrypt "$backup_file"
    
    if [ ! -f "$temp_gz" ]; then
        echo "❌ Decryption failed for ${db_name}"
        return 1
    fi
    
    echo "🔌 Terminating existing connections to ${db_name}..."
    docker exec -i -e PGPASSWORD="$DB_PASS" "$CENTRAL_POSTGRES_CONTAINER" psql -U "$DB_USER" -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${db_name}' AND pid <> pg_backend_pid();"

    echo "🗑️  Dropping and Recreating Database ${db_name}..."
    docker exec -i -e PGPASSWORD="$DB_PASS" "$CENTRAL_POSTGRES_CONTAINER" psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS ${db_name};"
    docker exec -i -e PGPASSWORD="$DB_PASS" "$CENTRAL_POSTGRES_CONTAINER" psql -U "$DB_USER" -d postgres -c "CREATE DATABASE ${db_name};"
    
    echo "📥 Importing Data..."
    zcat "$temp_gz" | docker exec -i -e PGPASSWORD="$DB_PASS" "$CENTRAL_POSTGRES_CONTAINER" psql -U "$DB_USER" -d "$db_name" > /dev/null 2>&1
    
    echo "🧹 Cleaning up temp files..."
    rm "$temp_gz"
    
    echo "✅ ${db_name} Restored Successfully!"
}

# Restore ISS
restore_db "$ISS_BACKUP" "iss_wbs"

# Restore StudioCentos
restore_db "$SC_BACKUP" "studiocentos"

echo "---------------------------------------------------"
echo "✨ All operations completed."

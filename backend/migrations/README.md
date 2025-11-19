# Database Migrations

This directory contains database migration scripts for the application.

## Migration Files

Each migration has two files:
- `XXX_migration_name.sql` - Raw SQL migration (for reference/manual application)
- `XXX_migration_name.py` - Python script for automatic migration

## Available Migrations

### 001_add_email_audit_log
- **Created**: 2025-11-13
- **Description**: Adds `email_audit_log` table for tracking sent emails
- **Model**: `app.common.models.EmailAuditLog`

### 002_add_gear_tables
- **Created**: 2025-11-19
- **Description**: Adds `gear_containers` and `gear_items` tables for gear management
- **Models**: `app.modules.gear.db_models.GearContainerDB`, `app.modules.gear.db_models.GearItemDB`

## Usage

### Option 1: Automatic Table Creation (Recommended for Development)

If you're using `init_db()` in development, the tables are created automatically from SQLAlchemy models:

```python
from app.core.database import init_db

await init_db()  # Creates all tables including email_audit_log
```

### Option 2: Run Python Migration Script

Apply specific migration:

```bash
cd backend
source ../.venv/bin/activate
python migrations/001_add_email_audit_log.py upgrade
```

Rollback migration:

```bash
python migrations/001_add_email_audit_log.py downgrade
```

### Option 3: Manual SQL Migration

For production environments, you may want to review and apply SQL manually:

```bash
# PostgreSQL
psql -d your_database -f migrations/001_add_email_audit_log.sql

# SQLite
sqlite3 your_database.db < migrations/001_add_email_audit_log.sql
```

## Migration History

| Version | Date       | Description                | Status |
|---------|------------|----------------------------|--------|
| 001     | 2025-11-13 | Add email_audit_log table  | ✓      |
| 002     | 2025-11-19 | Add gear tables            | ✓      |

## Future: Setting Up Alembic

For production, consider initializing Alembic for better migration management:

```bash
cd backend
source ../.venv/bin/activate

# Initialize Alembic
alembic init alembic

# Edit alembic.ini and alembic/env.py to configure database URL
# Then generate migrations:
alembic revision --autogenerate -m "Add email_audit_log table"

# Apply migrations:
alembic upgrade head
```

## Notes

- The email audit log system is enabled by default (`EMAIL_ENABLE_AUDIT=true`)
- Audit logging wraps any email adapter (SMTP, File, etc.)
- Email bodies are stored in the database for compliance (configurable)
- Failed emails can be retried using the retry mechanism

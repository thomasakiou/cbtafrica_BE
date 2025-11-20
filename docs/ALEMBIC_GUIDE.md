# Alembic Database Migration Guide

## Overview
This project now uses **Alembic** for database migrations. Alembic provides version control for your database schema, making it easy to track changes, upgrade databases, and roll back if needed.

## Prerequisites
- Python virtual environment activated
- PostgreSQL database running
- `.env` file configured with correct `DATABASE_URL`

## Quick Reference

### Common Commands

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Check current migration status
alembic current

# View migration history
alembic history --verbose

# Create a new migration (auto-generate from model changes)
alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>

# Show SQL that would be executed (dry run)
alembic upgrade head --sql
```

## Initial Setup (Already Completed)

The project has been configured with:
1. ✅ Alembic initialized (`alembic/` directory)
2. ✅ `alembic.ini` configured to use project settings
3. ✅ `alembic/env.py` configured to use app models
4. ✅ Initial migration created capturing current schema
5. ✅ Database stamped with current revision
6. ✅ `explanation_image` column migration included

## Workflow for Adding New Features

### 1. Modify Your Models
Edit files in `app/infrastructure/database/models.py`:

```python
# Example: Adding a new column
class Question(Base):
    __tablename__ = "questions"
    # ... existing columns ...
    new_column = Column(String, nullable=True)  # Your new field
```

### 2. Generate Migration
```bash
alembic revision --autogenerate -m "Add new_column to questions"
```

This will create a new file in `alembic/versions/` with upgrade/downgrade functions.

### 3. Review the Migration
Open the generated file in `alembic/versions/` and verify the changes:

```python
def upgrade() -> None:
    op.add_column('questions', sa.Column('new_column', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('questions', 'new_column')
```

### 4. Apply Migration
```bash
alembic upgrade head
```

### 5. Verify Migration
```bash
alembic current
# Should show the new revision ID
```

## Current Migration State

**Initial Migration**: `edd93bda6b69`
- Captures all existing tables (users, questions, tests, attempts, answers, etc.)
- Includes the new `explanation_image` column in questions table

## Migration Files

```
alembic/
├── versions/
│   └── edd93bda6b69_initial_migration_with_all_existing_.py
├── env.py          # Alembic environment configuration
├── script.py.mako  # Template for new migrations
└── README          # Alembic documentation
```

## Important Notes

### Database URL Configuration
- The database URL is automatically pulled from `app.config.settings.DATABASE_URL`
- No need to manually edit `alembic.ini` for database credentials
- Use `.env` file to configure database connection

### Auto-generation Limitations
Alembic auto-generate can detect:
- ✅ Added/removed tables
- ✅ Added/removed columns
- ✅ Changed column types (with some limitations)
- ✅ Added/removed indexes

Alembic auto-generate **cannot** detect:
- ❌ Renamed tables (appears as drop + add)
- ❌ Renamed columns (appears as drop + add)
- ❌ Changes to constraints in some cases

**Always review generated migrations before applying!**

## Troubleshooting

### Migration Conflicts
If you get conflicts or errors:

```bash
# Check current state
alembic current

# View all revisions
alembic history

# If needed, manually stamp to a specific revision
alembic stamp <revision_id>
```

### Reset Migrations (Nuclear Option)
⚠️ **Use with caution!** This will lose migration history.

```bash
# 1. Backup your database!
pg_dump cbt_db > backup.sql

# 2. Drop all tables
# (Run in psql or your database tool)

# 3. Remove alembic_version table
DROP TABLE alembic_version;

# 4. Create tables fresh
python -c "from app.infrastructure.database.models import Base; from app.infrastructure.database.connection import engine; Base.metadata.create_all(bind=engine)"

# 5. Stamp with current revision
alembic stamp head
```

### View Raw SQL
To see what SQL will be executed without applying:

```bash
alembic upgrade head --sql > migration.sql
```

## Production Deployment

### Before Deploying
1. **Test migrations locally** with a copy of production data
2. **Backup production database**
3. **Review all pending migrations**
4. **Check for data loss** (dropping columns, etc.)

### Deployment Steps
```bash
# 1. Stop the application (or put in maintenance mode)
sudo systemctl stop cbt

# 2. Backup database
pg_dump cbt_db > backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Apply migrations
cd /root/cbtafrica_BE
source venv/bin/activate
alembic upgrade head

# 4. Verify migration succeeded
alembic current

# 5. Start application
sudo systemctl start cbt

# 6. Check logs
sudo journalctl -u cbt -f
```

### Rollback Plan
If something goes wrong:

```bash
# Quick rollback to previous version
alembic downgrade -1

# Or restore from backup
psql cbt_db < backup_20251109_120000.sql
```

## CI/CD Integration

Add to your deployment script:

```bash
#!/bin/bash
set -e  # Exit on error

echo "Activating virtual environment..."
source venv/bin/activate

echo "Applying database migrations..."
alembic upgrade head

echo "Restarting application..."
sudo systemctl restart cbt

echo "Deployment complete!"
```

## Examples

### Example: Adding a New Table

1. **Add model** in `models.py`:
```python
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(Text)
```

2. **Generate migration**:
```bash
alembic revision --autogenerate -m "Add categories table"
```

3. **Review and apply**:
```bash
# Review the generated file first
cat alembic/versions/<new_revision>_add_categories_table.py

# Apply
alembic upgrade head
```

### Example: Modifying a Column

1. **Update model**:
```python
# Change from:
explanation = Column(Text, default="No Explanation")
# To:
explanation = Column(Text, nullable=False, default="")
```

2. **Generate and apply**:
```bash
alembic revision --autogenerate -m "Make explanation non-nullable"
alembic upgrade head
```

## Best Practices

1. **Always review** auto-generated migrations before applying
2. **Test locally** before applying to production
3. **Use descriptive messages** for migration files
4. **Keep migrations small** and focused on one change
5. **Never edit applied migrations** - create a new one to fix issues
6. **Commit migrations to git** along with model changes
7. **Document complex migrations** with comments in the migration file

## Migration Naming Convention

Use clear, descriptive names:
- ✅ `"Add explanation_image to questions"`
- ✅ `"Create categories table"`
- ✅ `"Add user_role index"`
- ❌ `"Update database"`
- ❌ `"Fix stuff"`

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Auto-generate Reference](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

# Alembic Setup - Quick Start Guide

## ✅ Alembic Successfully Configured!

Alembic has been set up and configured for this project. The database migration system is now ready to use.

## What Was Done

1. ✅ **Initialized Alembic** - Created `alembic/` directory structure
2. ✅ **Configured alembic.ini** - Set to use project settings for database URL
3. ✅ **Updated env.py** - Connected to your SQLAlchemy models and settings
4. ✅ **Created initial migration** - Captured current database state including:
   - All existing tables (users, questions, tests, attempts, answers, etc.)
   - The new `explanation_image` column in questions table
5. ✅ **Stamped database** - Marked database as being at current revision
6. ✅ **Updated main.py** - Removed auto-create, now uses Alembic exclusively
7. ✅ **Added documentation** - Created comprehensive guides

## Current State

**Migration Revision**: `edd93bda6b69` (head)
**Status**: Database is up to date
**New Field**: `explanation_image` column added to questions table

## Daily Workflow

### When You Add/Modify Database Models

```bash
# 1. Modify your models in app/infrastructure/database/models.py
# Example: Add a new column or table

# 2. Generate migration
source venv/bin/activate
alembic revision --autogenerate -m "Add new_field to table_name"

# 3. Review the generated migration file
# Check: alembic/versions/<new_revision>_add_new_field_to_table_name.py

# 4. Apply the migration
alembic upgrade head

# 5. Verify it worked
alembic current
```

## Essential Commands

```bash
# Check current migration status
alembic current

# View all migrations
alembic history

# Create new migration after model changes
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# See what SQL would be executed (dry run)
alembic upgrade head --sql
```

## Files Created/Modified

### New Files
- `alembic.ini` - Alembic configuration
- `alembic/env.py` - Environment setup
- `alembic/versions/edd93bda6b69_*.py` - Initial migration
- `docs/ALEMBIC_GUIDE.md` - Detailed documentation
- `docs/ALEMBIC_QUICKSTART.md` - This file

### Modified Files
- `main.py` - Removed `Base.metadata.create_all()`, now uses Alembic
- `README.md` - Added migration instructions
- `.gitignore` - Added upload directory rules

## Testing the Setup

### Test 1: Check Status
```bash
cd /root/cbtafrica_BE
source venv/bin/activate
alembic current
```
**Expected output**: `edd93bda6b69 (head)`

### Test 2: View History
```bash
alembic history
```
**Expected output**: Shows initial migration with explanation_image

### Test 3: Verify Database
```bash
psql -d cbt_db -c "\d questions"
```
**Expected output**: Should show `explanation_image` column

## Production Deployment Checklist

When deploying to production:

- [ ] Backup production database
- [ ] Test migrations on a copy of production data
- [ ] Review all pending migrations
- [ ] Stop application
- [ ] Run `alembic upgrade head`
- [ ] Verify migration succeeded
- [ ] Start application
- [ ] Monitor logs for errors

## Troubleshooting

### "Target database is not up to date"
```bash
alembic upgrade head
```

### "Multiple heads detected"
```bash
alembic merge <revision1> <revision2> -m "merge heads"
alembic upgrade head
```

### "Can't locate revision"
```bash
# Check current state
alembic current

# If needed, manually set
alembic stamp head
```

## Important Notes

1. **Never edit applied migrations** - Create a new migration to fix issues
2. **Always commit migrations to git** - They're part of your code
3. **Test locally first** - Don't apply untested migrations to production
4. **Review auto-generated code** - Alembic isn't perfect, check the migrations
5. **Keep migrations small** - One logical change per migration

## Next Steps

### For Developers
1. Read `docs/ALEMBIC_GUIDE.md` for detailed instructions
2. Practice creating a test migration
3. Learn the rollback process

### For Deployment
1. Add migration step to deployment script
2. Set up backup process before migrations
3. Create rollback procedures

## Example: Creating Your First Migration

```bash
# 1. Modify a model
# Add this to app/infrastructure/database/models.py in User class:
# profile_image = Column(String, nullable=True)

# 2. Generate migration
alembic revision --autogenerate -m "Add profile_image to users"

# 3. Review the generated file
cat alembic/versions/<new_revision>_add_profile_image_to_users.py

# 4. Apply it
alembic upgrade head

# 5. Verify
alembic current
psql -d cbt_db -c "\d users"
```

## Getting Help

- **Detailed Guide**: See `docs/ALEMBIC_GUIDE.md`
- **Alembic Docs**: https://alembic.sqlalchemy.org/
- **Tutorial**: https://alembic.sqlalchemy.org/en/latest/tutorial.html

## Success Indicators

✅ `alembic current` shows the head revision
✅ `explanation_image` column exists in questions table
✅ No errors when running migrations
✅ Application starts successfully

---

**Status**: ✅ Ready to use!
**Last Updated**: 2025-11-09
**Current Revision**: edd93bda6b69

dev: ; docker-compose up --build

# Create a PostgreSQL backup using pg_dump. Requires DATABASE_URL
# environment variable in libpq format, e.g. postgres://user:pass@host:5432/db
backup: ; @test -n "$$DATABASE_URL" || (echo "DATABASE_URL is not set" && exit 1); pg_dump $$DATABASE_URL > backup.sql

# Restore a PostgreSQL backup previously created with make backup.
# Will overwrite existing data in the target database.
restore: ; @test -n "$$DATABASE_URL" || (echo "DATABASE_URL is not set" && exit 1); psql $$DATABASE_URL < backup.sql

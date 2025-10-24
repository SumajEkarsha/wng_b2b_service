#!/bin/bash

# Create a new Alembic migration
if [ -z "$1" ]; then
    echo "Usage: ./scripts/create_migration.sh 'migration message'"
    exit 1
fi

alembic revision --autogenerate -m "$1"

#!/bin/bash

# Script to run the seed.py file with proper environment setup
# This script should be run from the wng_b2b_service directory

echo "=========================================="
echo "Running Database Seed Script"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please run this script from the wng_b2b_service directory"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Run the seed script
echo "🌱 Starting database seeding..."
echo ""

python scripts/seed.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Database seeding completed successfully!"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "❌ Database seeding failed!"
    echo "=========================================="
    exit 1
fi

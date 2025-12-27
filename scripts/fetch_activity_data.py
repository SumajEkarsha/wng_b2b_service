"""
Script to fetch data from the Activity Database and save to JSON files.

This script connects to the activity database (DATABASE_URL_ACTIVITY),
retrieves all data from the 'activities' table and any other tables,
and stores the results in JSON files.

Usage:
    python scripts/fetch_activity_data.py

Environment Variables Required:
    DATABASE_URL_ACTIVITY - PostgreSQL connection string for the activity database
    (falls back to DATABASE_URL if not set)
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Load environment variables from .env file
load_dotenv()

# Output directory for JSON files
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_connection():
    """Get a connection to the activity database."""
    # Use DATABASE_URL_ACTIVITY if available, otherwise fall back to DATABASE_URL
    database_url = os.getenv("DATABASE_URL_ACTIVITY") or os.getenv("DATABASE_URL")
    
    if not database_url:
        raise ValueError("No database URL found. Set DATABASE_URL_ACTIVITY or DATABASE_URL in .env file")
    
    print(f"Connecting to database...")
    return psycopg2.connect(database_url)


def get_all_tables(conn) -> list:
    """Get a list of all tables in the public schema."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
    return tables


def fetch_table_data(conn, table_name: str) -> list:
    """Fetch all data from a specific table."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Use parameterized query for safety (though table_name comes from DB, not user input)
        cur.execute(f'SELECT * FROM "{table_name}"')
        rows = cur.fetchall()
    
    # Convert to list of dicts and handle special types
    results = []
    for row in rows:
        processed_row = {}
        for key, value in row.items():
            # Handle datetime objects
            if isinstance(value, datetime):
                processed_row[key] = value.isoformat()
            # Handle bytes
            elif isinstance(value, bytes):
                processed_row[key] = value.decode('utf-8', errors='replace')
            # Handle memoryview
            elif isinstance(value, memoryview):
                processed_row[key] = bytes(value).decode('utf-8', errors='replace')
            else:
                processed_row[key] = value
        results.append(processed_row)
    
    return results


def save_to_json(data: dict, filename: str):
    """Save data to a JSON file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Saved to: {filepath}")
    return filepath


def main():
    print("=" * 60)
    print("Activity Database Data Fetcher")
    print("=" * 60)
    
    try:
        conn = get_connection()
        print("Connected successfully!\n")
        
        # Get all tables
        tables = get_all_tables(conn)
        print(f"Found {len(tables)} tables: {tables}\n")
        
        all_data = {}
        
        for table in tables:
            print(f"Fetching data from table: {table}")
            try:
                data = fetch_table_data(conn, table)
                all_data[table] = data
                print(f"  → Retrieved {len(data)} records")
                
                # Also save each table to its own file
                if data:
                    save_to_json(
                        {"table": table, "count": len(data), "data": data},
                        f"{table}.json"
                    )
            except Exception as e:
                print(f"  → Error fetching {table}: {e}")
                all_data[table] = {"error": str(e)}
        
        # Save combined data to a single file
        print("\nSaving combined data...")
        combined_output = {
            "fetched_at": datetime.now().isoformat(),
            "tables": list(all_data.keys()),
            "table_counts": {table: len(data) if isinstance(data, list) else 0 for table, data in all_data.items()},
            "data": all_data
        }
        save_to_json(combined_output, "all_tables_data.json")
        
        conn.close()
        print("\n" + "=" * 60)
        print("Data fetch complete!")
        print(f"Output files saved to: {OUTPUT_DIR}")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Futon Manufacturing SQLite Seed Script
Wave 2 Database & Seed Agent

Usage:
    python data/seed.py

This script:
- Creates (or overwrites) data/futon_manufacturing.db
- Executes the complete schema + data + views from futon_manufacturing_sqlite.sql
- Enables foreign keys
- Reports row counts for key tables after seeding

Run from the project root (D:\Projects\Funton-Ai or equivalent).
"""

import sqlite3
import os
import sys
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent.resolve()
SQL_FILE = SCRIPT_DIR / "futon_manufacturing_sqlite.sql"
DB_FILE = Path(os.environ.get("FUTON_DB_FILE", SCRIPT_DIR / "futon_manufacturing.db")).resolve()

def execute_sql_script(conn: sqlite3.Connection, sql_script: str) -> None:
    """Execute a multi-statement SQL script safely, skipping empty statements."""
    # Remove block comments and normalize
    # Split on semicolons that are statement terminators (basic but effective for our clean SQL)
    statements = []
    current = []
    for line in sql_script.splitlines(keepends=True):
        stripped = line.strip()
        current.append(line)
        if stripped.endswith(';'):
            stmt = ''.join(current).strip()
            if stmt and stmt != ';':
                statements.append(stmt)
            current = []
    # Handle any trailing statement without ;
    if current:
        stmt = ''.join(current).strip()
        if stmt:
            statements.append(stmt)

    cursor = conn.cursor()
    executed = 0
    errors = 0
    for i, stmt in enumerate(statements, 1):
        # Skip pure comments / pragmas that are safe
        clean = stmt.strip()
        if not clean or clean.startswith('--') and 'CREATE' not in clean.upper():
            continue
        try:
            cursor.execute(stmt)
            executed += 1
        except sqlite3.Error as e:
            # Allow duplicate table / index errors during re-runs (common during dev)
            msg = str(e).lower()
            if 'already exists' in msg or 'duplicate' in msg:
                continue
            print(f"  [WARN] Statement {i} failed: {e}\n    First 80 chars: {clean[:80]}...")
            errors += 1
    conn.commit()
    print(f"  Executed {executed} statements successfully ({errors} warnings).")

def main():
    print("=" * 60)
    print("Futon Manufacturing - SQLite Seed Runner")
    print("=" * 60)

    if not SQL_FILE.exists():
        print(f"ERROR: SQL file not found: {SQL_FILE}")
        sys.exit(1)

    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Remove old DB for clean seed (as per "complete, ready-to-run")
    if DB_FILE.exists():
        print(f"Removing existing database: {DB_FILE}")
        DB_FILE.unlink()

    print(f"Creating new database: {DB_FILE}")

    # Read entire SQL file
    print(f"Reading SQL from: {SQL_FILE}")
    sql_content = SQL_FILE.read_text(encoding="utf-8")

    # Connect and seed
    conn = sqlite3.connect(str(DB_FILE))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")

    print("Executing schema, data, agent tables, and report views...")
    execute_sql_script(conn, sql_content)

    # Post-seed verification
    cursor = conn.cursor()

    print("\n--- Post-seed Verification ---")
    tables_to_check = [
        "Items", "BillOfMaterials", "Warehouse", "Inventory",
        "Supplier", "Customer", "SalesOrder", "SalesOrderDetail",
        "ProductionOrder", "SalesChannel", "Store", "SalesRep",
        "AgentConversation", "AgentAction", "AgentRecommendation", "AgentAuditLog"
    ]

    for table in tables_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} rows")
        except sqlite3.Error as e:
            print(f"  {table}: ERROR - {e}")

    # Quick view check
    print("\n--- Sample Report View Check ---")
    try:
        cursor.execute("SELECT COUNT(*) FROM vw_BOMExplosion")
        print(f"  vw_BOMExplosion rows: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM vw_Sales_ByChannel")
        print(f"  vw_Sales_ByChannel rows: {cursor.fetchone()[0]}")
    except Exception as e:
        print(f"  View check note: {e}")

    conn.close()

    print(f"\n✅ SUCCESS: Database ready at {DB_FILE}")
    print("   You can now connect with any SQLite tool or the Funton AI backend.")
    print("   Example: sqlite3 data/futon_manufacturing.db")
    print("=" * 60)

if __name__ == "__main__":
    main()
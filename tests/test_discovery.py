# tests/test_discovery.py
import sqlite3
import pytest
import sectio

def test_internal_resource_path():
    """
    Verifies that Sectio can find its own internal database.
    """
    # We use the internal helper we just defined in __init__.py
    path = sectio._get_db_path()
    
    print(f"\n📍 Testing resource at: {path}")
    
    import os
    assert os.path.exists(path), f"Resource database missing at {path}"

def test_database_connection():
    """
    Verifies that the internal database is a valid SQLite file and accessible.
    """
    path = sectio._get_db_path()
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    # Simple query to check connectivity
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    
    assert len(tables) > 0, "Connected to DB, but no tables found."

def test_catalog_integration():
    """
    Verifies that the high-level Catalog can list the families from the internal DB.
    """
    families = sectio.catalog.list_families()
    
    print(f"\n📂 Catalog Discovery: Found {len(families)} families")
    for fam in sorted(families):
        print(f"  - {fam}")
    
    assert "IPE" in families
    assert "RHS" in families

def test_metadata_consistency():
    """
    Checks if the data_dictionary table is present in the internal resource.
    """
    path = sectio._get_db_path()
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM data_dictionary")
    count = cursor.fetchone()[0]
    conn.close()
    
    print(f"📖 Metadata rows: {count}")
    assert count > 0, "Data dictionary is empty in internal resource."


def test_metadata_uniques():
    """
    Analyzes the data_dictionary to show unique engineering properties.
    """
    path = sectio._get_db_path()
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    # Get unique column names and their descriptions
    cursor.execute("""
        SELECT DISTINCT column_name, description, unit 
        FROM data_dictionary 
        ORDER BY column_name ASC
    """)
    uniques = cursor.fetchall()
    conn.close()
    
    print(f"\n💎 Found {len(uniques)} Unique Engineering Properties:")
    # Formatting as a small table for readability
    print(f"{'Property':<15} | {'Unit':<10} | {'Description'}")
    print("-" * 60)
    for prop, desc, unit in uniques:
        print(f"{prop:<15} | {unit:<10} | {desc}")
    
    assert len(uniques) > 0
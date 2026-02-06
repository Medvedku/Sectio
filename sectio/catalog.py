import sqlite3
import pandas as pd
import os

class Catalog:
    def __init__(self, db_path):
        self.db_path = db_path

    def list_families(self):
        """Returns a list of all table names (IPE, HEA, RHS, etc.)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'sections_%'")
            return [row[0].replace("sections_", "").upper() for row in cursor.fetchall()]

    def get_family(self, family_name):
        """Returns a Pandas DataFrame of an entire table (e.g., all IPEs)"""
        table_name = f"sections_{family_name.lower()}"
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

    def search(self, query):
        """Searches across all tables for a partial string (e.g., '200')"""
        results = []
        families = self.list_families()
        with sqlite3.connect(self.db_path) as conn:
            for fam in families:
                table = f"sections_{fam.lower()}"
                df = pd.read_sql_query(
                    f"SELECT Section_ID FROM {table} WHERE Section_ID LIKE ?", 
                    conn, params=(f"%{query}%",)
                )
                for _, row in df.iterrows():
                    results.append({"Family": fam, "ID": row['Section_ID']})
        return pd.DataFrame(results)



    def get_schema(self, family_name=None):
            """
            Returns property definitions. 
            If no family_name: Returns unique column definitions across the whole DB.
            If family_name: Returns definitions specific to that family's table.
            """
            with sqlite3.connect(self.db_path) as conn:
                if not family_name:
                    # Get unique definitions across all tables
                    query = "SELECT DISTINCT column_name, description, unit FROM DATA_DICTIONARY"
                    return pd.read_sql_query(query, conn)
                
                # Filter specifically by the requested table
                table_key = f"sections_{family_name.lower()}"
                query = "SELECT column_name, description, unit FROM DATA_DICTIONARY WHERE table_name = ?"
                return pd.read_sql_query(query, conn, params=(table_key,))
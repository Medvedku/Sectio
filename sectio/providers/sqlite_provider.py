# sectio/providers/sqlite_provider.py
import sqlite3
import pandas as pd
from sectio.registry import GEOM_MAP, PARAM_MAP
from shapely import affinity
from ..core import CrossSection

class SQLiteProvider:
    """
    The data adapter for Sectio that connects the internal SQLite database 
    to the Shapely geometry engine.
    """
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_section(self, table_name: str, section_id: str, subdivision: str = 'calc'):
        """
        Fetches a section by ID from a specific table, maps its columns 
        to geometry arguments, and returns a Shapely Polygon.
        
        Args:
            table_name (str): The name of the table in the DB (e.g., 'sections_ipe').
            section_id (str): The unique ID of the profile (e.g., 'IPE 200').
            subdivision (str/int): Resolution for arcs ('calc', 'draft', or int).
            
        Returns:
            shapely.geometry.Polygon: The generated cross-section geometry.
        """
        table_name = table_name.lower()
        # 1. Validation: Ensure the table is registered in registry.py
        if table_name not in GEOM_MAP or table_name not in PARAM_MAP:
            raise ValueError(
                f"Table '{table_name}' is not registered in Sectio. "
                "Check sectio/registry.py for supported tables."
            )

        # 2. Database Fetching
        # We use pandas because it handles NULL/NaN values gracefully and 
        # converts SQL rows into accessible dictionaries easily.
        with sqlite3.connect(self.db_path) as conn:
            query = f"SELECT * FROM {table_name} WHERE Section_ID = ? COLLATE NOCASE"
            df = pd.read_sql_query(query, conn, params=(section_id,))

        if df.empty:
            raise ValueError(f"Section '{section_id}' not found in table '{table_name}'.")

        # Extract the first row as a dictionary-like object
        row = df.iloc[0]

        # 3. Dynamic Function Mapping
        # Look up which drawing function and which parameter map to use
        draw_func = GEOM_MAP[table_name]
        param_config = PARAM_MAP[table_name]

        # 4. Building the argument dictionary
        # We translate DB column names (e.g., 'tf') into function arguments (e.g., 'tf')
        func_args = {}
        for func_arg, db_col in param_config.items():
            val = row.get(db_col)
            # Ensure value is a float for Shapely/Numpy; handle NaNs as 0.0
            func_args[func_arg] = float(val) if pd.notna(val) else 0.0
        # 5. Geometry Generation
        # 'cs' stands for CrossSection; it contains the polygon and j_manual
        cs = draw_func(**func_args, subdivision=subdivision, section_id=section_id)
        
        # Center the polygon at its centroid
        # We access the polygon attribute inside the cs object
        cx, cy = cs.polygon.centroid.x, cs.polygon.centroid.y
        centered_poly = affinity.translate(cs.polygon, xoff=-cx, yoff=-cy)

        # Re-wrap in a new CrossSection object with the centered geometry
        return CrossSection(polygon=centered_poly, metadata=row.to_dict(), j_manual=cs._j_manual)
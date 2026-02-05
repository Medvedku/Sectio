import importlib.resources
from pathlib import Path

def get_db_path():
    """
    Locates the steel_profiles.db file within the package resources.
    """
    # This works in Python 3.9+
    try:
        # 'sectio.resources' is the sub-package, 'steel_profiles.db' is the file
        with importlib.resources.path("sectio.resources", "steel_profiles.db") as p:
            return str(p)
    except Exception:
        # Fallback for local development if resources aren't yet recognized
        return str(Path(__file__).parent / "resources" / "steel_profiles.db")


# sectio/utils.py
import re

def sanitize_filename(name: str) -> str:
    """
    Standardizes section names into filesystem-safe strings.
    Replaces spaces, dots, and slashes with underscores or dashes.
    Example: 'CHS 33.7/2.6' -> 'CHS_33_7-2_6'
    """
    # Replace spaces and dots with underscores
    name = name.replace(" ", "_").replace(".", "_")
    # Replace slashes with dashes (to avoid directory navigation errors)
    name = name.replace("/", "-").replace("\\", "-")
    
    # Optional: remove any other non-alphanumeric chars (except _ and -)
    name = re.sub(r'[^a-zA-Z0-9_\-]', '', name)
    
    return name
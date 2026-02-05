# sectio/__init__.py
import importlib.resources
from pathlib import Path

# 1. Geometry Functions (Low-level API)
from .geometry import (
    create_i_section_geometry, 
    create_rhs_geometry, 
    create_angle_geometry,
    create_chs_geometry,
    create_shs_geometry,
    create_t_section_geometry,
    create_u_section_geometry,
    create_upn_section_geometry,
    create_ue_section_geometry,
    create_ipn_section_geometry
)

# 2. Providers and Catalog (Data Access API)
from .providers.sqlite_provider import SQLiteProvider
from .providers.svg_provider import SVGProvider
from .catalog import Catalog

# 3. Exporters and Utilities
from .exporters.svg_exporter import save_geometry_to_svg
from .utils import sanitize_filename

# 4. Internal Resource Management
def _get_db_path():
    """Locates the internal steel database resource."""
    try:
        # Modern Python 3.9+ resource access
        path_resource = importlib.resources.files("sectio.resources") / "steel_profiles.db"
        return str(path_resource)
    except Exception:
        # Fallback for local development
        return str(Path(__file__).parent / "resources" / "steel_profiles.db")

# 5. Global API Instances
# We instantiate these so the user can use 'sectio.db' or 'sectio.catalog' directly.
_default_db_path = _get_db_path()

db = SQLiteProvider(_default_db_path)
catalog = Catalog(_default_db_path)
# Pointing to 'tests/testing_sections' as a default for your current workflow
svg = SVGProvider(search_path="tests/testing_sections")

__version__ = "0.1.0"
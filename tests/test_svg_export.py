import pytest
import sectio
import os
import random

def test_random_section_to_svg():
    # 1. Selection
    families = sectio.catalog.list_families()
    random_family = random.choice(families)
    
    df = sectio.catalog.get_family(random_family)
    random_row = df.sample(n=1).iloc[0]
    section_id = random_row['Section_ID']
    
    print(f"\n🎲 Selected: {section_id} (Family: {random_family})")
    
    # 2. Geometry Generation
    table_name = f"sections_{random_family.lower()}"
    geom = sectio.db.get_section(table_name, section_id)
    
    # 3. Path Setup
    # Sanitize filename: replace / with _ and remove spaces
    safe_id = section_id.replace("/", "_").replace(" ", "_")
    filename = f"{safe_id}.svg"
    output_folder = "tests/exported_svgs"
    
    # 4. Export using the new module path
    from sectio.exporters.svg_exporter import save_geometry_to_svg
    
    save_geometry_to_svg(
        geom.polygon, 
        filename=filename, 
        folder=output_folder, 
        color="#2ecc71" # Structural Green
    )
    
    # 5. Assert
    full_path = os.path.join(output_folder, filename)
    assert os.path.exists(full_path)
    print(f"✅ SVG verified at: {full_path}")
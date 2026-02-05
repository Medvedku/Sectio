import sectio
import os

def test_raw_chs_export():
    # 1. Fetch the specific CHS section
    section_id = "CHS33.7x2.6"
    
    # We use the provider to get the geometry
    # Table name for CHS is 'sections_chs'
    geom = sectio.db.get_section("sections_chs", section_id)
    
    # 2. Define the raw filename
    # We aren't sanitizing, just appending the extension
    raw_filename = f"{section_id}.svg"
    output_folder = "tests/exported_svgs"
    
    print(f"\n🧪 Attempting raw export with filename: '{raw_filename}'")
    
    # 3. Export using your existing function
    from sectio.exporters.svg_exporter import save_geometry_to_svg
    
    try:
        save_geometry_to_svg(
            geom, 
            filename=raw_filename, 
            folder=output_folder,
            color="#34495e" # A dark steel grey
        )
        
        full_path = os.path.join(output_folder, raw_filename)
        if os.path.exists(full_path):
            print(f"✅ Success! File created at: {full_path}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")


def test_hollow_sections_export():
    output_folder = "tests/exported_svgs"
    
    # 1. RHS Sample (Rectangular)
    rhs_id = "RHS50x30x2.6"
    rhs_geom = sectio.db.get_section("sections_rhs", rhs_id)
    sectio.save_geometry_to_svg(rhs_geom, f"{rhs_id}.svg", folder=output_folder, color="#3498db")

    # 2. SHS Sample (Square)
    shs_id = "SHS40x2.6"
    shs_geom = sectio.db.get_section("sections_shs", shs_id)
    sectio.save_geometry_to_svg(shs_geom, f"{shs_id}.svg", folder=output_folder, color="#9b59b6")

    print(f"\n📂 Exported {rhs_id} and {shs_id} to {output_folder}")


if __name__ == "__main__":
    test_raw_chs_export()



import sectio

def test_svg_ingestion():
    # Load the handwritten logo / custom showcase section
    profile_custom = sectio.svg.get_section("sectio2.svg")
    
    print(f"\n🎨 Ingested SVG: {profile_custom.geom_type}")
    print(f"📏 Calculated Area: {profile_custom.area:.2f} mm²")
    
    # Check if the section is hollow
    num_holes = len(profile_custom.interiors)
    is_hollow = num_holes > 0
    
    print(f"🕳️ Status: {'HOLLOW' if is_hollow else 'SOLID'}")
    print(f"🔢 Total internal holes detected: {num_holes}")
    
    # Optional: Print extreme fiber distances (helpful for FEA)
    minx, miny, maxx, maxy = profile_custom.bounds
    print(f"📐 Bounds: Width {(maxx-minx):.2f}mm, Height {(maxy-miny):.2f}mm")
    
    assert profile_custom.area > 0
    # Since it's a showcase logo with multiple holes, we just verify it's not solid
    assert is_hollow, "Showcase SVG should have at least one hole!"
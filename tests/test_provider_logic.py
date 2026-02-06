import sectio

def test_ipe_provider():
    # This uses the 'db' instance created in sectio/__init__.py
    geom = sectio.db.get_section("sections_ipe", "IPE200")
    
    print(f"\nIPE 200 successfully generated.")
    print(f"Calculated Area: {geom.area:.2f} mm²")
    
    assert geom.area > 0
    assert geom.polygon.geom_type == 'Polygon'
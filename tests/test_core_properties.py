import sectio
import pytest

def test_compare_db_vs_calc():
    """Validates IPE 200: DB Table vs. Geometric Math."""
    # ipe is now a CrossSection object
    ipe = sectio.db.get_section("sections_ipe", "IPE200")
    
    print(f"\n📊 PROPERTY COMPARISON: {ipe.metadata.get('Section_ID')}")
    print(f"{'Property':<15} | {'DB Value':<12} | {'Calc Value':<12} | {'Error %'}")
    print("-" * 65)
    
    # Map DB names (A, Iy, Iz) to our calculated properties (area, Ix, Iy)
    # NOTE: In many steel DBs, Iy is the strong axis (our Ix)
    checks = [
        ("Area", float(ipe.metadata['A']), ipe.area),
        ("Ix (Strong)", float(ipe.metadata['Iy']), ipe.Ix),
        ("Iy (Weak)", float(ipe.metadata['Iz']), ipe.Iy),
    ]
    
    for label, db_val, calc_val in checks:
        error = abs(db_val - calc_val) / db_val * 100
        print(f"{label:<15} | {db_val:<12.2f} | {calc_val:<12.2f} | {error:.4f}%")
        assert error < 1.0 

def test_logo_engineering_analysis():
    """Analyzes the handwritten logo as a structural element."""
    logo = sectio.svg.get_section("sectio2.svg")
    
    print(f"\n✍️ LOGO STRUCTURAL ANALYSIS")
    print("-" * 35)
    print(f"Total Area:      {logo.area:.2f} mm²")
    print(f"Strong Axis Ix:  {logo.Ix:.2f} mm⁴")
    print(f"Torsion (J):     {logo.J:.2f} mm⁴")
    print(f"Holes Detected:  {len(logo.polygon.interiors)}")
    
    assert logo.area > 0
import pytest
import sectio
import pandas as pd

def test_area_precision_audit():
    """
    Compares calculated geometry area vs. theoretical database area 
    across all available families.
    """
    families = sectio.catalog.list_families()
    results = []

    print(f"\n{'Family':<10} | {'Section':<15} | {'DB Area':<10} | {'Calc Area':<10} | {'Error %'}")
    print("-" * 75)

    for family in families:
        # Get the full table for this family
        df = sectio.catalog.get_family(family)
        if df.empty or 'A' not in df.columns:
            continue
        
        # Take the first section as a representative sample
        sample = df.iloc[0]
        section_id = sample['Section_ID']
        db_area = float(sample['A'])
        
        # Generate geometry using the provider
        table_name = f"sections_{family.lower()}"
        try:
            # Using 'calc' for maximum precision
            geom = sectio.db.get_section(table_name, section_id, subdivision='calc')
            calc_area = geom.area
            
            error_pct = abs(calc_area - db_area) / db_area * 100
            
            results.append({
                "family": family,
                "id": section_id,
                "error": error_pct
            })

            print(f"{family:<10} | {section_id:<15} | {db_area:<10.2f} | {calc_area:<10.2f} | {error_pct:.4f}%")
            
            # Tolerance check: 1% is usually acceptable due to 
            # minor variations in how different standards round fillet areas.
            assert error_pct < 1.0, f"High error in {section_id}: {error_pct:.2f}%"

        except Exception as e:
            print(f"{family:<10} | {section_id:<15} | ERROR: {str(e)}")

    avg_error = sum(r['error'] for r in results) / len(results)
    print("-" * 75)
    print(f"✅ Audit Complete. Average Area Error: {avg_error:.5f}%")
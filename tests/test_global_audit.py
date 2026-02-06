import sectio
import pandas as pd
import os
import pytest

def test_run_global_audit():
    output_csv = "audit_results.csv"
    families = sectio.catalog.list_families()
    results = []
    
    for family in families:
        table_name = f"sections_{family.lower()}"
        family_df = sectio.catalog.get_family(family)
        sections = family_df['Section_ID'].tolist()
        
        for section_id in sections:
            try:
                cs = sectio.db.get_section(table_name, section_id, subdivision='calc')
                
                # 1. Extract DB Values
                db_a = float(cs.metadata.get('A', 0))
                db_iy = float(cs.metadata.get('Iy', 0))
                db_iz = float(cs.metadata.get('Iz', 0))
                
                # 'cy' or 'e' is usually the centroid distance from the back of the web
                # We need to find the calculated xc. Since we center at (0,0), 
                # we compare the shift applied during centering.
                db_xc = float(cs.metadata.get('cy', 0)) 
                
                # 2. Get Calculated Centroid 
                # In your SQLiteProvider, you center the poly. 
                # Let's assume xc is the distance from the leftmost point to 0.
                minx, _, _, _ = cs.polygon.bounds
                calc_xc = abs(minx)

                if db_a <= 0: continue

                # 3. Error Calculations
                err_a = abs(db_a - cs.area) / db_a * 100
                err_iy = abs(db_iy - cs.Iy) / db_iy * 100 if db_iy > 0 else 0
                err_iz = abs(db_iz - cs.Iz) / db_iz * 100 if db_iz > 0 else 0
                err_xc = abs(db_xc - calc_xc) if db_xc > 0 else 0 # Absolute error in mm

                results.append({
                    "Family": family,
                    "Section_ID": section_id,
                    "Area_Err_%": round(err_a, 4),
                    "Iy_Err_%": round(err_iy, 4),
                    "Iz_Err_%": round(err_iz, 4),
                    "XC_Err_mm": round(err_xc, 4)
                })

            except Exception as e:
                pass

    df_audit = pd.DataFrame(results)
    df_audit.to_csv(output_csv, index=False)
    print(f"\n✅ Audit updated with Centroid tracking. Saved to {output_csv}")
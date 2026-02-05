import sectio

def test_inspect_lu_outliers():
    family = "sections_lu"
    # Target our suspicious sections and their immediate siblings
    targets = [
        "L160x100x12", "L160x100x14", "L160x100x16", # Neighbors of the 160x100
        "L75x50x5", "L75x50x6", "L75x50x7"             # Neighbors of the 75x50
    ]
    
    print(f"\n{'Section':<15} | {'Calc Ix':<10} | {'Calc Iy':<10} | {'DB Iy':<10} | {'DB Iz':<10}")
    print("-" * 75)

    for sid in targets:
        try:
            cs = sectio.db.get_section(family, sid)
            # Local Ix/Iy (Calculated) vs DB Iy/Iz
            db_y = float(cs.metadata.get('Iy', 0))
            db_z = float(cs.metadata.get('Iz', 0))
            
            # We also check the principal moments I1/I2 (Imax/Imin) 
            # in case the DB is mixing local and principal axes.
            i1, i2 = cs.principal_moments
            
            print(f"{sid:<15} | {cs.Ix:10.0f} | {cs.Iy:10.0f} | {db_y:10.0f} | {db_z:10.0f}")
            # print(f"{'':<15} | Prin I1: {i1:10.0f} | Prin I2: {i2:10.0f}")
            print("-" * 75)
        except Exception:
            print(f"{sid:<15} | Not found")

if __name__ == "__main__":
    test_inspect_lu_outliers()
import os
from shapely import affinity


def save_geometry_to_svg(geom, filename, folder=".", invert_y=True, color="#66cb99"):
    """
    Saves a shapely geometry to an SVG file with mm units, supporting hollow sections.
    """
    # 1. Handle Y-axis inversion
    if invert_y:
        geom = affinity.scale(geom, yfact=-1, origin='center')

    # 2. Get Bounds
    minx, miny, maxx, maxy = geom.bounds
    width_val = maxx - minx
    height_val = maxy - miny

    # 3. Construct Path Data for Shell AND Holes
    # Start with the exterior (the shell)
    path_strings = []
    
    # Process the outer boundary
    ext_coords = "M " + " L ".join([f"{x},{y}" for x, y in geom.exterior.coords]) + " Z"
    path_strings.append(ext_coords)

    # Process all internal holes
    for interior in geom.interiors:
        int_coords = "M " + " L ".join([f"{x},{y}" for x, y in interior.coords]) + " Z"
        path_strings.append(int_coords)

    # Combine all paths into one 'd' attribute
    # SVG 'fill-rule: evenodd' or 'nonzero' will handle the holes automatically
    full_path_str = " ".join(path_strings)

    # 4. Handle Directory Management
    if not os.path.exists(folder):
        os.makedirs(folder)

    full_path = os.path.join(folder, filename)

    # 5. Build SVG content 
    # Added 'fill-rule="evenodd"' to ensure holes are punched out regardless of winding
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" 
                    viewBox="{minx} {miny} {width_val} {height_val}" 
                    width="{width_val}mm" height="{height_val}mm">
                    <path d="{full_path_str}" fill="{color}" fill-rule="evenodd" stroke="none" />
                    </svg>"""

    # 6. Save to file
    with open(full_path, "w") as f:
        f.write(svg_content)

    print(f"Saved: {full_path} ({width_val:.2f}mm x {height_val:.2f}mm)")
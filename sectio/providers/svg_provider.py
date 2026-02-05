import os
import numpy as np
import svgelements
from shapely.geometry import Polygon
from shapely import affinity
from sectio.core import CrossSection


class SVGProvider:
    def __init__(self, search_path: str = "."):
        self.search_path = search_path

    def get_section(self, filename: str):
        """
        Loads an SVG and builds a centered, scaled Polygon.
        """
        full_path = os.path.join(self.search_path, filename)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"SVG not found at {full_path}")

        # 1. Parse using svgelements
        svg_data = svgelements.SVG.parse(full_path)
        
        # 2. Get the header width (the viewBox width from Inkscape)
        header_width = svg_data.viewbox.width
        
        # 3. Build the polygon using your logic
        return self._build_polygon(svg_data, header_width)

    def _build_polygon(self, svg_data, header_width):
        all_loops = []
        FLATTEN_STEPS = 128 # Your preferred resolution

        for element in svg_data.elements():
            if not isinstance(element, svgelements.Path):
                continue

            for subpath in element.as_subpaths():
                points = []
                for segment in subpath:
                    if isinstance(segment, svgelements.Move):
                        if segment.end is not None:
                            points.append((segment.end.x, segment.end.y))
                        continue

                    if isinstance(segment, (svgelements.Line, svgelements.Close)):
                        if segment.end is not None:
                            points.append((segment.end.x, segment.end.y))
                    else:
                        for t in np.linspace(0, 1, FLATTEN_STEPS)[1:]:
                            try:
                                p = segment.point(t)
                                points.append((p.x, p.y))
                            except (AttributeError, TypeError):
                                continue

                if len(points) >= 3:
                    # Your clean_points logic
                    clean_points = [points[0]]
                    for i in range(1, len(points)):
                        if points[i] != points[i-1]:
                            clean_points.append(points[i])

                    if len(clean_points) >= 3:
                        poly = Polygon(clean_points)
                        if poly.is_valid and poly.area > 1e-6:
                            all_loops.append(poly)

        if not all_loops:
            raise ValueError("No valid geometry loops found in SVG.")

        # Sorting: Largest is the Shell
        all_loops.sort(key=lambda p: p.area, reverse=True)
        shell = all_loops[0].exterior
        holes = [p.exterior for p in all_loops[1:] if all_loops[0].contains(p)]

        poly = Polygon(shell=shell, holes=holes)

        # --- Scale and Flip ---
        minx, _, maxx, _ = poly.bounds
        raw_w = maxx - minx
        
        if raw_w == 0:
            return poly

        # This is where the magic happens
        scale = header_width / raw_w
        
        # Flip Y (SVG Y-down to Engineering Y-up)
        poly = affinity.scale(poly, xfact=scale, yfact=-scale, origin=(0, 0))

        # Center at (0,0)
        cx, cy = poly.centroid.x, poly.centroid.y
        poly = affinity.translate(poly, xoff=-cx, yoff=-cy)
        return CrossSection(polygon=poly)
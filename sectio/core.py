import numpy as np
from shapely.geometry import Polygon
import meshpy.triangle as triangle


class CrossSection:
    def __init__(self, polygon, metadata=None, j_manual=None):
        # Step 1: Auto-convert list of points to a Polygon if needed
        if isinstance(polygon, (list, tuple)):
            self.polygon = Polygon(polygon)
        else:
            self.polygon = polygon
            
        self.metadata = metadata or {}
        self._j_manual = j_manual
        
        # Step 2: Now .bounds will never fail
        minx, miny, maxx, maxy = self.polygon.bounds
        self.x_left = abs(minx)
        self.x_right = maxx
        self.y_bottom = abs(miny)
        self.y_top = maxy

    # --- Basic Properties ---
    @property
    def area(self):
        return self.polygon.area

    @property
    def has_holes(self):
        return len(self.polygon.interiors) > 0


    def _calculate_raw_inertia(self):
            def _poly_inertia(ring):
                x, y = ring.coords.xy
                # Initialize inside the helper
                iy_sum, iz_sum, iyz_sum = 0.0, 0.0, 0.0
                
                for i in range(len(x) - 1):
                    # Segment common factor (Shoelace area component)
                    common = x[i] * y[i+1] - x[i+1] * y[i]
                    
                    iy_sum += (y[i]**2 + y[i]*y[i+1] + y[i+1]**2) * common
                    iz_sum += (x[i]**2 + x[i]*x[i+1] + x[i+1]**2) * common
                    iyz_sum += (x[i]*y[i+1] + 2*x[i]*y[i] + 2*x[i+1]*y[i+1] + x[i+1]*y[i]) * common
                
                # Return the raw sums for this specific ring
                return abs(iy_sum / 12.0), abs(iz_sum / 12.0), iyz_sum / 24.0

            # 1. Start with the exterior shell
            Iy, Iz, Iyz = _poly_inertia(self.polygon.exterior)

            # 2. Subtract the holes (interiors)
            for interior in self.polygon.interiors:
                h_iy, h_iz, h_iyz = _poly_inertia(interior)
                Iy -= h_iy
                Iz -= h_iz
                Iyz -= h_iyz
                
            return Iy, Iz, Iyz

    @property
    def Iy(self): return self._calculate_raw_inertia()[0]
    
    @property
    def Iz(self): return self._calculate_raw_inertia()[1]
    
    @property
    def Iyz(self): return self._calculate_raw_inertia()[2]

    # --- Principal Axes ---
    @property
    def principal_moments(self):
        iy, iz, iyz = self.Iy, self.Iz, self.Iyz
        avg_i = (iy + iz) / 2
        diff_i = np.sqrt(((iy - iz) / 2)**2 + iyz**2)
        return avg_i + diff_i, avg_i - diff_i

    @property
    def alpha(self):
        """Inclination to principal axis in degrees."""
        iy, iz, iyz = self.Iy, self.Iz, self.Iyz
        return 0.5 * np.degrees(np.arctan2(2 * iyz, iz - iy))

    # --- Section Moduli ---
    @property
    def elastic_moduli(self):
        """Returns (Wy_top, Wy_bot, Wz_right, Wz_left)"""
        wy_top = self.Iy / self.y_top if self.y_top > 0 else 0
        wy_bot = self.Iy / self.y_bottom if self.y_bottom > 0 else 0
        wz_right = self.Iz / self.x_right if self.x_right > 0 else 0
        wz_left = self.Iz / self.x_left if self.x_left > 0 else 0
        return wy_top, wy_bot, wz_right, wz_left


    def mesh_section(self, max_area=1.0):
        import meshpy.triangle as triangle
        points = []
        facets = []
        
        # Helper to add a loop (exterior or interior) to the mesh info
        def add_loop(coords):
            start_idx = len(points)
            new_points = list(coords)[:-1]
            points.extend(new_points)
            for i in range(len(new_points)):
                facets.append((start_idx + i, start_idx + (i + 1) % len(new_points)))

        # 1. Add Exterior
        add_loop(self.polygon.exterior.coords)
        
        # 2. Add Interiors and identify hole points
        holes = []
        if self.has_holes:
            for interior in self.polygon.interiors:
                add_loop(interior.coords)
                # Use the centroid of the hole as the "exclusion point"
                from shapely.geometry import Polygon
                hole_poly = Polygon(interior)
                holes.append((hole_poly.centroid.x, hole_poly.centroid.y))

        # 3. Define mesh info
        info = triangle.MeshInfo()
        info.set_points(points)
        info.set_facets(facets)
        if holes:
            info.set_holes(holes) # This is the magic line
        
        # 4. Build mesh
        mesh = triangle.build(info, max_volume=max_area)
        return mesh


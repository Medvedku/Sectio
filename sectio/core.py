import numpy as np
from shapely.geometry import Polygon

class CrossSection:
    def __init__(self, polygon, metadata=None):
        self.polygon = polygon
        self.metadata = metadata or {}
        
        # Fiber distances from Centroid (0,0)
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

    # # --- Inertia Calculation (Your logic integrated) ---
    # def _calculate_raw_inertia(self):
    #     def _poly_inertia(ring):
    #         x, y = ring.coords.xy
    #         iy, iz, iyz = 0, 0, 0
    #         for i in range(len(x) - 1):
    #             a_i = x[i] * y[i+1] - x[i+1] * y[i]
    #             iy += (y[i]**2 + y[i]*y[i+1] + y[i+1]**2) * a_i
    #             iz += (x[i]**2 + x[i]*x[i+1] + x[i+1]**2) * a_i
    #             iyz += (x[i]*y[i+1] + 2*x[i]*y[i] + 2*x[i+1]*y[i+1] + x[i+1]*y[i]) * a_i
    #         return abs(iy / 12.0), abs(iz / 12.0), iyz / 24.0
    #
    #     Iy, Iz, Iyz = _poly_inertia(self.polygon.exterior)
    #     for interior in self.polygon.interiors:
    #         h_iy, h_iz, h_iyz = _poly_inertia(interior)
    #         Iy -= h_iy
    #         Iz -= h_iz
    #         Iyz -= h_iyz
    #     return Iy, Iz, Iyz

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

    @property
    def J(self):
        """Torsional Constant (St. Venant)."""
        if self.has_holes:
            area_int = sum(Polygon(h).area for h in self.polygon.interiors)
            area_mean = ( (self.area + area_int) + area_int ) / 2
            peri_mean = (self.polygon.exterior.length + sum(h.length for h in self.polygon.interiors)) / 2
            t_eff = self.area / peri_mean
            return (4 * (area_mean**2) * t_eff) / peri_mean
        else:
            avg_t = self.area / ( (self.polygon.exterior.length + sum(h.length for h in self.polygon.interiors)) / 2)
            return (1/3) * self.area * (avg_t**2)
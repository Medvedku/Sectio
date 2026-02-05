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
    #         ix, iy, ixy = 0, 0, 0
    #         for i in range(len(x) - 1):
    #             a_i = x[i] * y[i+1] - x[i+1] * y[i]
    #             ix += (y[i]**2 + y[i]*y[i+1] + y[i+1]**2) * a_i
    #             iy += (x[i]**2 + x[i]*x[i+1] + x[i+1]**2) * a_i
    #             ixy += (x[i]*y[i+1] + 2*x[i]*y[i] + 2*x[i+1]*y[i+1] + x[i+1]*y[i]) * a_i
    #         return abs(ix / 12.0), abs(iy / 12.0), ixy / 24.0

    #     Ix, Iy, Ixy = _poly_inertia(self.polygon.exterior)
    #     for interior in self.polygon.interiors:
    #         h_ix, h_iy, h_ixy = _poly_inertia(interior)
    #         Ix -= h_ix
    #         Iy -= h_iy
    #         Ixy -= h_ixy
    #     return Ix, Iy, Ixy

    def _calculate_raw_inertia(self):
            def _poly_inertia(ring):
                x, y = ring.coords.xy
                # Initialize inside the helper
                ix_sum, iy_sum, ixy_sum = 0.0, 0.0, 0.0
                
                for i in range(len(x) - 1):
                    # Segment common factor (Shoelace area component)
                    common = x[i] * y[i+1] - x[i+1] * y[i]
                    
                    ix_sum += (y[i]**2 + y[i]*y[i+1] + y[i+1]**2) * common
                    iy_sum += (x[i]**2 + x[i]*x[i+1] + x[i+1]**2) * common
                    ixy_sum += (x[i]*y[i+1] + 2*x[i]*y[i] + 2*x[i+1]*y[i+1] + x[i+1]*y[i]) * common
                
                # Return the raw sums for this specific ring
                return abs(ix_sum / 12.0), abs(iy_sum / 12.0), ixy_sum / 24.0

            # 1. Start with the exterior shell
            Ix, Iy, Ixy = _poly_inertia(self.polygon.exterior)

            # 2. Subtract the holes (interiors)
            for interior in self.polygon.interiors:
                h_ix, h_iy, h_ixy = _poly_inertia(interior)
                Ix -= h_ix
                Iy -= h_iy
                Ixy -= h_ixy
                
            return Ix, Iy, Ixy

    @property
    def Ix(self): return self._calculate_raw_inertia()[0]
    
    @property
    def Iy(self): return self._calculate_raw_inertia()[1]
    
    @property
    def Ixy(self): return self._calculate_raw_inertia()[2]

    # --- Principal Axes ---
    @property
    def principal_moments(self):
        ix, iy, ixy = self.Ix, self.Iy, self.Ixy
        avg_i = (ix + iy) / 2
        diff_i = np.sqrt(((ix - iy) / 2)**2 + ixy**2)
        return avg_i + diff_i, avg_i - diff_i

    @property
    def alpha(self):
        """Inclination to principal axis in degrees."""
        ix, iy, ixy = self.Ix, self.Iy, self.Ixy
        return 0.5 * np.degrees(np.arctan2(2 * ixy, iy - ix))

    # --- Section Moduli ---
    @property
    def elastic_moduli(self):
        """Returns (Wx_top, Wx_bot, Wy_right, Wy_left)"""
        wx_top = self.Ix / self.y_top if self.y_top > 0 else 0
        wx_bot = self.Ix / self.y_bottom if self.y_bottom > 0 else 0
        wy_right = self.Iy / self.x_right if self.x_right > 0 else 0
        wy_left = self.Iy / self.x_left if self.x_left > 0 else 0
        return wx_top, wx_bot, wy_right, wy_left

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
"""AquaAlert AI — Agent 2: Terrain & Drainage Service.

Provides environmental terrain and drainage characteristics for geographical
grids and localized coordinates.
"""

from typing import List, Optional
from backend.contracts import GridCell
from data.terrain.grid_generator import generate_pilot_grid


class TerrainService:
    """Service providing terrain and stormwater drainage geospatial layers."""

    def get_grid_cells(self, area_name: str = "Delhi NCR") -> List[GridCell]:
        """Retrieve standardized grid cells for an administrative region.

        Args:
            area_name: Target pilot area.

        Returns:
            List of populated GridCell objects.
        """
        return generate_pilot_grid(area_name)

    def get_cell_by_id(self, cell_id: str, area_name: str = "Delhi NCR") -> Optional[GridCell]:
        """Find a single grid cell by its unique ID.

        Args:
            cell_id: Grid cell identifier (e.g. 'DEL_01').
            area_name: Target pilot area.

        Returns:
            Matching GridCell if found, None otherwise.
        """
        cells = self.get_grid_cells(area_name)
        for c in cells:
            if c.cell_id == cell_id:
                return c
        return None

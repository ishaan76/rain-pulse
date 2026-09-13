"""AquaAlert AI — Agent 2: Terrain & Drainage Service.

Provides environmental terrain and drainage characteristics for geographical
grids and localized coordinates.
"""

from typing import List, Optional

from backend.contracts import GridCell
from data.terrain.grid_generator import generate_greater_noida_grid, generate_pilot_grid

# Areas served from the hand-authored demo dataset in grid_generator.py.
# Kept for offline demo-mode reliability (AGENTS.md rule 15); these are
# NOT derived from Copernicus DEM / OSM.
DEMO_PILOT_AREAS = {"Delhi NCR", "Noida", "Gurugram", "Ghaziabad"}

# Areas served from live real-data acquisition (Copernicus DEM + OSM).
REAL_DATA_AREAS = {"Greater Noida"}


class TerrainDataUnavailableError(RuntimeError):
    """Raised when real terrain data (DEM/OSM) is required but unreachable.

    Deliberately not caught-and-faked: per project rules, terrain values
    must never be fabricated as a fallback for a missing live source.
    """


class TerrainService:
    """Service providing terrain and stormwater drainage geospatial layers."""

    def get_grid_cells(self, area_name: str = "Delhi NCR") -> List[GridCell]:
        """Retrieve standardized grid cells for an administrative region.

        Args:
            area_name: Target pilot area. "Greater Noida" is served from
                live Copernicus DEM + OSM acquisition; the other pilot
                areas are served from the fixed offline demo dataset.

        Returns:
            List of populated GridCell objects.

        Raises:
            TerrainDataUnavailableError: If `area_name` requires live
                Copernicus DEM/OSM data and that data cannot be fetched
                (e.g. no network access or upstream service error).
        """
        if area_name in REAL_DATA_AREAS:
            try:
                return generate_greater_noida_grid()
            except Exception as exc:  # re-raised as a typed, documented error
                raise TerrainDataUnavailableError(
                    f"Could not retrieve real terrain data for {area_name!r}: {exc}. "
                    "Live Copernicus DEM (OpenTopoData) and OSM (Overpass API) access "
                    "is required for this area; no fabricated fallback is used."
                ) from exc
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
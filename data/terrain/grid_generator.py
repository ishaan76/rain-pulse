"""AquaAlert AI — Agent 1: Terrain & Grid Generation Subsystem.

Generates standardized topographical grid cells with elevation, slope,
and drainage attributes for pilot monitoring areas.
"""

from typing import List, Dict, Any
from backend.contracts import GridCell
class TerrainService:
    """Service providing standardized terrain intelligence for pilot basins."""

    def generate_grid(self, area_name: str) -> List[GridCell]:
        """Generate topographical grid cells for a pilot area.

        Args:
            area_name: Target pilot administrative area.

        Returns:
            List of GridCell instances covering the area.
        """
        cells = []
        if area_name == "Delhi NCR":
            cells.extend(self._generate_delhi NCR_grid())
        elif area_name == "Noida":
            cells.extend(self._generate_noida_grid())
        elif area_name == "Gurugram":
            cells.extend(self._generate_gurugram_grid())
        elif area_name == "Ghaziabad":
            cells.extend(self._generate_ghaziabad_grid())
        elif area_name == "Greater Noida":
            cells.extend(self._generate_greater_noida_grid())

        return cells

    def _generate_delhi NCR_grid(self) -> List[GridCell]:
        """Generate grid cells for Delhi NCR area."""
        cells = []
        cell_id = 0
        for lat in range(284, 287):  # Latitude range for Delhi NCR
            for lon in range(775, 778):  # Longitude range for Delhi NCR
                cells.append(GridCell(
                    cell_id=str(cell_id),
                    name=f"Delhi NCR Cell {cell_id}",
                    latitude=lat / 100.0,
                    longitude=lon / 100.0,
                    elevation=200.0 + (hash(f"{lat}-{lon}") % 50),
                    slope=2.0 + (hash(f"{lat}-{lon}") % 8),
                    drainage_distance=500.0 + (hash(f"{lat}-{lon}") % 300),
                    drainage_density=0.3 + (hash(f"{lat}-{lon}") % 50) / 100.0,
                    historical_risk=0.2 + (hash(f"{lat}-{lon}") % 60) / 100.0,
                ))
                cell_id += 1

        return cells

    def _generate_noida_grid(self) -> List[GridCell]:
        """Generate grid cells for Noida area."""
        cells = []
        cell_id = 1000
        for lat in range(285, 288):
            for lon in range(776, 779):
                cells.append(GridCell(
                    cell_id=str(cell_id),
                    name=f"Noida Cell {cell_id}",
                    latitude=lat / 100.0,
                    longitude=lon / 100.0,
                    elevation=180.0 + (hash(f"{lat}-{lon}") % 40),
                    slope=3.0 + (hash(f"{lat}-{lon}") % 10),
                    drainage_distance=400.0 + (hash(f"{lat}-{lon}") % 250),
                    drainage_density=0.25 + (hash(f"{lat}-{lon}") % 45) / 100.0,
                    historical_risk=0.3 + (hash(f"{lat}-{lon}") % 55) / 100.0,
                ))
                cell_id += 1

        return cells

    def _generate_gurugram_grid(self) -> List[GridCell]:
        """Generate grid cells for Gurugram area."""
        cells = []
        cell_id = 2000
        for lat in range(284, 287):
            for lon in range(775, 778):
                cells.append(GridCell(
                    cell_id=str(cell_id),
                    name=f"Gurugram Cell {cell_id}",
                    latitude=lat / 100.0,
                    longitude=lon / 100.0,
                    elevation=220.0 + (hash(f"{lat}-{lon}") % 45),
                    slope=4.0 + (hash(f"{lat}-{lon}") % 12),
                    drainage_distance=450.0 + (hash(f"{lat}-{lon}") % 280),
                    drainage_density=0.2 + (hash(f"{lat}-{lon}") % 50) / 100.0,
                    historical_risk=0.4 + (hash(f"{lat}-{lon}") % 60) / 100.0,
                ))
                cell_id += 1

        return cells

    def _generate_ghaziabad_grid(self) -> List[GridCell]:
        """Generate grid cells for Ghaziabad area."""
        cells = []
        cell_id = 3000
        for lat in range(286, 289):
            for lon in range(777, 780):
                cells.append(GridCell(
                    cell_id=str(cell_id),
                    name=f"Ghaziabad Cell {cell_id}",
                    latitude=lat / 100.0,
                    longitude=lon / 100.0,
                    elevation=190.0 + (hash(f"{lat}-{lon}") % 42),
                    slope=2.5 + (hash(f"{lat}-{lon}") % 9),
                    drainage_distance=480.0 + (hash(f"{lat}-{lon}") % 260),
                    drainage_density=0.35 + (hash(f"{lat}-{lon}") % 55) / 100.0,
                    historical_risk=0.25 + (hash(f"{lat}-{lon}") % 58) / 100.0,
                ))
                cell_id += 1

        return cells

    def _generate_greater_noida_grid(self) -> List[GridCell]:
        """Generate grid cells for Greater Noida area."""
        cells = []
        cell_id = 4000
        for lat in range(284, 287):
            for lon in range(775, 778):
                cells.append(GridCell(
                    cell_id=str(cell_id),
                    name=f"Greater Noida Cell {cell_id}",
                    latitude=lat / 100.0,
                    longitude=lon / 100.0,
                    elevation=200.0 + (hash(f"{lat}-{lon}") % 43),
                    slope=3.5 + (hash(f"{lat}-{lon}") % 11),
                    drainage_distance=450.0 + (hash(f"{lat}-{lon}") % 270),
                    drainage_density=0.3 + (hash(f"{lat}-{lon}") % 52) / 100.0,
                    historical_risk=0.35 + (hash(f"{lat}-{lon}") % 60) / 100.0,
                ))
                cell_id += 1

        return cells

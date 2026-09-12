# Agent 2 — Terrain & Drainage Subsystem Playbook

## Responsibility
Build and maintain geospatial features relating to topography, elevation, slope, and drainage network infrastructure.

## Owned Files & Folders
- `data/terrain/elevation.py`: Elevation modeling and slope calculation logic.
- `data/terrain/drainage.py`: Proximity to trunk drains and drainage density scoring.
- `data/terrain/grid_generator.py`: Grid cell definitions for Delhi NCR, Noida, Gurugram, and Ghaziabad.
- `data/terrain/service.py`: `TerrainService` providing grid and localized cell lookup.
- `tests/test_terrain.py`: Agent 2 unit test suite.

## Interface Contract Output
Returns instances of `backend.contracts.GridCell`:
```python
@dataclass
class GridCell:
    cell_id: str
    name: str
    latitude: float
    longitude: float
    elevation: float
    slope: float
    drainage_distance: float
    drainage_density: float
    historical_risk: float
```

## How to Test
```bash
python -m pytest tests/test_terrain.py -v
```

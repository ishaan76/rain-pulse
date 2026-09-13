# Agent 2 — Terrain & Drainage Subsystem Playbook

## Responsibility
Build and maintain geospatial features relating to topography, elevation, slope, and drainage network infrastructure.

## Owned Files & Folders
- `data/terrain/elevation.py`: Elevation modeling and slope calculation logic.
- `data/terrain/drainage.py`: Proximity to trunk drains and drainage density scoring.
- `data/terrain/grid_generator.py`: Grid cell definitions for Delhi NCR, Noida, Gurugram, Ghaziabad (fixed offline demo dataset) and Greater Noida (live Copernicus DEM + OSM acquisition).
- `data/terrain/dem_client.py`: `CopernicusDEMClient` — real point-elevation lookups against Copernicus DEM GLO-30 via OpenTopoData.
- `data/terrain/osm_client.py`: `OSMDrainageClient` — real waterway/drain feature lookups via the OSM Overpass API.
- `data/terrain/service.py`: `TerrainService` providing grid and localized cell lookup.
- `tests/test_terrain.py`: Agent 2 unit test suite.

### Real data vs. demo data
- Delhi NCR / Noida / Gurugram / Ghaziabad are **fixed offline demo constants** (kept for guaranteed demo-mode reliability per AGENTS.md rule 15). They are NOT derived from DEM/OSM and should not be presented as such.
- Greater Noida is generated from **live** Copernicus DEM elevation samples and OSM drainage features via `generate_greater_noida_grid()`. If the live services are unreachable, `TerrainService.get_grid_cells("Greater Noida")` raises `TerrainDataUnavailableError` rather than fabricating values.
- Copernicus DEM GLO-30 is a **static** elevation product (no 0-6h refresh). It is valid for elevation/slope only; 0-6h dynamic hydrology must come from Agent 1 (rainfall) or a live gauge feed.

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

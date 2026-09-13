"""AquaAlert AI — Agent 2: Geospatial Grid Generator.

Generates standardized topographical grid cells with elevation, slope,
and drainage attributes for pilot monitoring areas.
"""

import math
from typing import Any, Dict, List, Optional, Tuple

from backend.contracts import GridCell
from data.terrain.elevation import calculate_slope

# --- Greater Noida: real-data-derived grid -------------------------------
#
# Unlike the PILOT_AREA_CELLS below (hand-authored demo constants kept for
# offline demo-mode reliability, per AGENTS.md rule 15), the Greater Noida
# grid is generated from live Copernicus DEM elevation samples and OSM
# drainage features. No elevation, slope, or drainage value here is
# invented, randomized, or hard-coded — see generate_greater_noida_grid().

GREATER_NOIDA_BBOX: Dict[str, float] = {"south": 28.40, "north": 28.55, "west": 77.40, "east": 77.55}
GREATER_NOIDA_GRID_SPACING_DEG = 0.02  # ~2.2 km cell pitch at this latitude
GREATER_NOIDA_SLOPE_NEIGHBOR_OFFSET_DEG = 0.01  # ~1.1 km east offset used for slope sampling
GREATER_NOIDA_DRAINAGE_SEARCH_RADIUS_M = 1000
GREATER_NOIDA_DRAINAGE_DENSITY_REFERENCE_COUNT = 8  # documented assumption, see below


PILOT_AREA_CELLS: Dict[str, List[Dict[str, Any]]] = {
    "Delhi NCR": [
        {"cell_id": "DEL_01", "name": "Minto Bridge Underpass", "lat": 28.6328, "lon": 77.2223, "elev": 198.0, "slope": 1.1, "drain_dist": 750.0, "drain_dens": 0.25, "hist_risk": 0.95},
        {"cell_id": "DEL_02", "name": "ITO Ring Road Junction", "lat": 28.6289, "lon": 77.2435, "elev": 204.0, "slope": 1.4, "drain_dist": 620.0, "drain_dens": 0.35, "hist_risk": 0.85},
        {"cell_id": "DEL_03", "name": "Kashmere Gate ISBT", "lat": 28.6675, "lon": 77.2300, "elev": 202.0, "slope": 1.3, "drain_dist": 580.0, "drain_dens": 0.30, "hist_risk": 0.80},
        {"cell_id": "DEL_04", "name": "AIIMS Flyover Depression", "lat": 28.5672, "lon": 77.2100, "elev": 215.0, "slope": 1.8, "drain_dist": 400.0, "drain_dens": 0.55, "hist_risk": 0.60},
        {"cell_id": "DEL_05", "name": "Connaught Place Inner Circle", "lat": 28.6315, "lon": 77.2167, "elev": 218.0, "slope": 2.2, "drain_dist": 300.0, "drain_dens": 0.70, "hist_risk": 0.40},
        {"cell_id": "DEL_06", "name": "Dhaula Kuan Ridge", "lat": 28.5921, "lon": 77.1607, "elev": 238.0, "slope": 4.5, "drain_dist": 250.0, "drain_dens": 0.80, "hist_risk": 0.20},
        {"cell_id": "DEL_07", "name": "Lajpat Nagar Ring Road", "lat": 28.5700, "lon": 77.2400, "elev": 208.0, "slope": 1.5, "drain_dist": 480.0, "drain_dens": 0.45, "hist_risk": 0.65},
        {"cell_id": "DEL_08", "name": "Sarai Kale Khan Basin", "lat": 28.5880, "lon": 77.2600, "elev": 201.0, "slope": 1.2, "drain_dist": 690.0, "drain_dens": 0.28, "hist_risk": 0.90},
    ],
    "Noida": [
        {"cell_id": "NOI_01", "name": "Sector 18 Commercial Hub", "lat": 28.5708, "lon": 77.3261, "elev": 196.0, "slope": 1.2, "drain_dist": 720.0, "drain_dens": 0.28, "hist_risk": 0.90},
        {"cell_id": "NOI_02", "name": "Sector 62 IT Park Lowland", "lat": 28.6271, "lon": 77.3725, "elev": 198.0, "slope": 1.4, "drain_dist": 550.0, "drain_dens": 0.40, "hist_risk": 0.75},
        {"cell_id": "NOI_03", "name": "Botanical Garden Underpass", "lat": 28.5644, "lon": 77.3343, "elev": 195.0, "slope": 1.0, "drain_dist": 680.0, "drain_dens": 0.32, "hist_risk": 0.85},
        {"cell_id": "NOI_04", "name": "Noida-Greater Noida Expressway", "lat": 28.5100, "lon": 77.3800, "elev": 202.0, "slope": 2.1, "drain_dist": 350.0, "drain_dens": 0.65, "hist_risk": 0.45},
        {"cell_id": "NOI_05", "name": "Sector 137 Residential Pocket", "lat": 28.5030, "lon": 77.4080, "elev": 199.0, "slope": 1.6, "drain_dist": 480.0, "drain_dens": 0.50, "hist_risk": 0.55},
        {"cell_id": "NOI_06", "name": "Sector 15A Yamuna Bank", "lat": 28.5850, "lon": 77.3100, "elev": 193.0, "slope": 0.9, "drain_dist": 820.0, "drain_dens": 0.20, "hist_risk": 0.95},
    ],
    "Gurugram": [
        {"cell_id": "GUR_01", "name": "Hero Honda Chowk Underpass", "lat": 28.4350, "lon": 77.0100, "elev": 218.0, "slope": 1.0, "drain_dist": 850.0, "drain_dens": 0.20, "hist_risk": 0.95},
        {"cell_id": "GUR_02", "name": "Subhash Chowk Junction", "lat": 28.4410, "lon": 77.0420, "elev": 221.0, "slope": 1.3, "drain_dist": 680.0, "drain_dens": 0.30, "hist_risk": 0.85},
        {"cell_id": "GUR_03", "name": "IFFCO Chowk", "lat": 28.4720, "lon": 77.0725, "elev": 226.0, "slope": 1.8, "drain_dist": 450.0, "drain_dens": 0.50, "hist_risk": 0.60},
        {"cell_id": "GUR_04", "name": "Golf Course Road Underpass", "lat": 28.4610, "lon": 77.1020, "elev": 224.0, "slope": 1.4, "drain_dist": 590.0, "drain_dens": 0.42, "hist_risk": 0.70},
        {"cell_id": "GUR_05", "name": "Cyber City Transit Hub", "lat": 28.4950, "lon": 77.0890, "elev": 230.0, "slope": 2.5, "drain_dist": 310.0, "drain_dens": 0.75, "hist_risk": 0.35},
        {"cell_id": "GUR_06", "name": "Badshahpur Drain Culvert", "lat": 28.4120, "lon": 77.0450, "elev": 214.0, "slope": 0.8, "drain_dist": 920.0, "drain_dens": 0.18, "hist_risk": 0.98},
    ],
    "Ghaziabad": [
        {"cell_id": "GHA_01", "name": "Mohan Nagar Crossing", "lat": 28.6750, "lon": 77.3820, "elev": 208.0, "slope": 1.2, "drain_dist": 710.0, "drain_dens": 0.26, "hist_risk": 0.88},
        {"cell_id": "GHA_02", "name": "Sahibabad Industrial Area", "lat": 28.6590, "lon": 77.3600, "elev": 206.0, "slope": 1.1, "drain_dist": 760.0, "drain_dens": 0.22, "hist_risk": 0.92},
        {"cell_id": "GHA_03", "name": "Raj Nagar Extension Lowland", "lat": 28.7120, "lon": 77.4200, "elev": 212.0, "slope": 1.5, "drain_dist": 540.0, "drain_dens": 0.40, "hist_risk": 0.65},
        {"cell_id": "GHA_04", "name": "Hindon Barrage Approach", "lat": 28.6650, "lon": 77.4100, "elev": 204.0, "slope": 0.9, "drain_dist": 880.0, "drain_dens": 0.20, "hist_risk": 0.94},
        {"cell_id": "GHA_05", "name": "Kavi Nagar Commercial Belt", "lat": 28.6700, "lon": 77.4600, "elev": 216.0, "slope": 2.4, "drain_dist": 350.0, "drain_dens": 0.68, "hist_risk": 0.35},
    ],
}


def generate_pilot_grid(area_name: str) -> List[GridCell]:
    """Build standardized GridCell contracts for a given pilot area.

    Args:
        area_name: Pilot area (e.g. 'Delhi NCR', 'Noida', 'Gurugram', 'Ghaziabad').

    Returns:
        List of typed GridCell objects.
    """
    raw_cells = PILOT_AREA_CELLS.get(area_name, PILOT_AREA_CELLS["Delhi NCR"])
    return [
        GridCell(
            cell_id=c["cell_id"],
            name=c["name"],
            latitude=c["lat"],
            longitude=c["lon"],
            elevation=c["elev"],
            slope=c["slope"],
            drainage_distance=c["drain_dist"],
            drainage_density=c["drain_dens"],
            historical_risk=c["hist_risk"],
        )
        for c in raw_cells
    ]


def _frange(start: float, stop: float, step: float) -> List[float]:
    """Generate an inclusive float range, rounded to avoid FP drift.

    Args:
        start: Range start (inclusive).
        stop: Range end (inclusive, subject to floating point tolerance).
        step: Increment between values.

    Returns:
        List of rounded float values from start to stop.
    """
    values = []
    current = start
    while current <= stop + 1e-9:
        values.append(round(current, 6))
        current += step
    return values


def _build_greater_noida_grid_coords(
    spacing_deg: float = GREATER_NOIDA_GRID_SPACING_DEG,
) -> List[Tuple[str, float, float]]:
    """Build a regular lat/lon grid of cell centers covering the Greater Noida AOI.

    Args:
        spacing_deg: Grid spacing in decimal degrees.

    Returns:
        List of (cell_id, latitude, longitude) tuples with no overlaps or
        gaps within the bounding box (regular rectangular tiling).
    """
    bbox = GREATER_NOIDA_BBOX
    lats = _frange(bbox["south"], bbox["north"], spacing_deg)
    lons = _frange(bbox["west"], bbox["east"], spacing_deg)
    coords = []
    idx = 1
    for lat in lats:
        for lon in lons:
            coords.append((f"GNO_{idx:02d}", lat, lon))
            idx += 1
    return coords


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute great-circle distance between two lat/lon points in meters."""
    radius_m = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius_m * math.asin(math.sqrt(a))


def _summarize_drainage_features(
    lat: float,
    lon: float,
    elements: List[Dict[str, Any]],
    search_radius_m: float = GREATER_NOIDA_DRAINAGE_SEARCH_RADIUS_M,
    density_reference_count: int = GREATER_NOIDA_DRAINAGE_DENSITY_REFERENCE_COUNT,
) -> Tuple[float, float]:
    """Derive (drainage_distance_m, drainage_density) from raw OSM elements.

    Args:
        lat: Cell center latitude.
        lon: Cell center longitude.
        elements: Raw Overpass elements (each with 'center' or 'lat'/'lon').
        search_radius_m: Radius the elements were queried within; used as
            the "no feature found" fallback distance.
        density_reference_count: Assumed feature count representing a
            "fully drained" (density = 1.0) cell. This is a documented
            heuristic, not a calibrated municipal standard, since no
            authoritative per-cell drainage-capacity dataset is available.

    Returns:
        Tuple of (nearest drainage distance in meters, density in 0.0-1.0).
    """
    distances = []
    for element in elements:
        center = element.get("center") or {"lat": element.get("lat"), "lon": element.get("lon")}
        el_lat, el_lon = center.get("lat"), center.get("lon")
        if el_lat is None or el_lon is None:
            continue
        distances.append(_haversine_m(lat, lon, el_lat, el_lon))

    if not distances:
        return float(search_radius_m), 0.0

    nearest = min(distances)
    # `elements` may span a much larger area than this single cell (e.g. a
    # whole-AOI bbox fetch shared across all cells) — density must only
    # count features actually within `search_radius_m` of THIS cell, not
    # every feature in the shared list, or every cell saturates to 1.0.
    nearby_count = sum(1 for d in distances if d <= search_radius_m)
    density = min(1.0, nearby_count / density_reference_count)
    return round(nearest, 1), round(density, 2)


def generate_greater_noida_grid(
    dem_client: Optional[Any] = None,
    osm_client: Optional[Any] = None,
    spacing_deg: float = GREATER_NOIDA_GRID_SPACING_DEG,
    neighbor_offset_deg: float = GREATER_NOIDA_SLOPE_NEIGHBOR_OFFSET_DEG,
) -> List[GridCell]:
    """Build Greater Noida GridCells from real Copernicus DEM + OSM data.

    Every cell's elevation is sampled directly from Copernicus DEM GLO-30,
    slope is computed (via `elevation.calculate_slope`) from that sample and
    an eastward neighbor sample, and drainage distance/density are derived
    from real OSM waterway/drain features near the cell center. No terrain
    value in the returned cells is fabricated.

    `historical_risk` cannot be derived from either source (no authoritative
    Greater Noida flood-history dataset is available) and is left at the
    contract's documented neutral default (0.5) rather than invented.

    Args:
        dem_client: Elevation client exposing `fetch_point_elevations`.
            Defaults to `CopernicusDEMClient()`.
        osm_client: Drainage client exposing `fetch_drainage_features_in_bbox`.
            Defaults to `OSMDrainageClient()`.
        spacing_deg: Grid spacing in decimal degrees.
        neighbor_offset_deg: Eastward offset used for the slope-sampling
            neighbor point.

    Returns:
        List of typed GridCell objects covering the Greater Noida AOI.

    Raises:
        DEMUnavailableError: If Copernicus DEM elevation data cannot be fetched.
        OSMUnavailableError: If OSM drainage features cannot be fetched from
            any configured Overpass mirror.
    """
    if dem_client is None:
        from data.terrain.dem_client import CopernicusDEMClient

        dem_client = CopernicusDEMClient()
    if osm_client is None:
        from data.terrain.osm_client import OSMDrainageClient

        osm_client = OSMDrainageClient()

    coords = _build_greater_noida_grid_coords(spacing_deg)

    # Batch-fetch center + eastward-neighbor elevations in one request.
    query_points: List[Tuple[float, float]] = []
    for _, lat, lon in coords:
        query_points.append((lat, lon))
        query_points.append((lat, lon + neighbor_offset_deg))
    elevations = dem_client.fetch_point_elevations(query_points)

    # Single bbox fetch for the whole AOI (not one Overpass call per cell) -
    # see osm_client.py's design note on why per-cell querying was dropped.
    margin = GREATER_NOIDA_DRAINAGE_SEARCH_RADIUS_M / 111320.0  # meters -> approx degrees
    lats = [lat for _, lat, _ in coords]
    lons = [lon for _, _, lon in coords]
    drainage_elements = osm_client.fetch_drainage_features_in_bbox(
        south=min(lats) - margin,
        west=min(lons) - margin,
        north=max(lats) + margin,
        east=max(lons) + margin,
    )

    cells = []
    for i, (cell_id, lat, lon) in enumerate(coords):
        elevation_center = elevations[2 * i]
        elevation_neighbor = elevations[2 * i + 1]
        neighbor_distance_m = _haversine_m(lat, lon, lat, lon + neighbor_offset_deg)
        slope = calculate_slope(elevation_center, elevation_neighbor, neighbor_distance_m)

        drainage_distance, drainage_density = _summarize_drainage_features(lat, lon, drainage_elements)

        cells.append(
            GridCell(
                cell_id=cell_id,
                name=f"Greater Noida Grid Cell {cell_id}",
                latitude=lat,
                longitude=lon,
                elevation=elevation_center,
                slope=slope,
                drainage_distance=drainage_distance,
                drainage_density=drainage_density,
                # No authoritative historical flood-record source available;
                # left at the contract's documented neutral default.
            )
        )
    return cells
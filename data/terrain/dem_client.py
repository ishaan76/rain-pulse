"""AquaAlert AI — Agent 2: Copernicus DEM Acquisition Client (OpenTopography).

Fetches genuine Copernicus DEM GLO-30 elevation data from OpenTopography's
official Global DEM API (https://opentopography.org/), using
`demtype=COP30` and `outputFormat=AAIGrid` (a plain-text ESRI ASCII Grid).
AAIGrid is used specifically so no GDAL/rasterio dependency is required to
parse the raster — it's read with the standard library + simple parsing.

Requires a free OpenTopography API key: register at
https://portal.opentopography.org/myopentopo and set it as the
OPENTOPOGRAPHY_API_KEY environment variable. Per project rule 9/10
("never hard-code secrets; use environment variables"), no key is ever
embedded in code.

NOTE ON PROVIDER HISTORY:
    An earlier version of this client used the free OpenTopoData public
    API (api.opentopodata.org). That service does NOT host the Copernicus
    dataset on its public tier (confirmed via a live 400 "Dataset
    'copernicus30' not in config" response) — only OpenTopoData
    self-hosted deployments with the Copernicus tiles downloaded support
    it. This client was rewritten to call OpenTopography's official COP30
    endpoint instead, which is the real Copernicus DEM GLO-30 source.

IMPORTANT — data freshness:
    Copernicus DEM GLO-30 is a STATIC elevation product derived from
    TanDEM-X radar acquisitions collected primarily between 2011-2015 and
    released in 2021-2022. It has no 0-6h (or even annual) refresh cycle.
    It must NOT be treated as a real-time or short-term hydrological data
    source (e.g. standing water extent, drain blockage, live flow). It is
    appropriate only for static terrain shape (elevation, derived slope),
    which changes on geological rather than hourly timescales. Any 0-6h
    dynamic hydrological signal for AquaAlert must come from Agent 1
    (rainfall/weather) and/or a live gauge/sensor feed, never from DEM.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import requests

OPENTOPOGRAPHY_ENDPOINT = "https://portal.opentopography.org/API/globaldem"
DEM_DATASET = "COP30"  # Copernicus DEM GLO-30
DEM_RESOLUTION_M = 30.0
DEM_CRS = "EPSG:4326"
DEM_OUTPUT_FORMAT = "AAIGrid"
DEFAULT_BBOX_MARGIN_DEG = 0.02


@dataclass
class DEMAcquisitionMetadata:
    """Provenance record for elevation data pulled from Copernicus DEM.

    Attributes:
        source: Human-readable description of the data source/API.
        dataset: Dataset identifier.
        resolution_m: Native ground sample distance of the DEM in meters.
        crs: Coordinate reference system of the returned coordinates.
        acquisition_note: Freshness/limitation caveat for this dataset.
    """

    source: str
    dataset: str
    resolution_m: float
    crs: str
    acquisition_note: str


class DEMUnavailableError(RuntimeError):
    """Raised when the Copernicus DEM service cannot be reached, is
    misconfigured (e.g. missing API key), or returns unparseable data."""


@dataclass
class _RasterGrid:
    """Minimal ESRI ASCII Grid (AAIGrid) raster, sampled by nearest cell.

    Attributes:
        ncols: Number of columns in the raster.
        nrows: Number of rows in the raster.
        xllcorner: Longitude of the lower-left corner.
        yllcorner: Latitude of the lower-left corner.
        cellsize: Cell size in decimal degrees.
        nodata_value: Sentinel value indicating no data.
        data: Row-major raster values, row 0 = northernmost row.
    """

    ncols: int
    nrows: int
    xllcorner: float
    yllcorner: float
    cellsize: float
    nodata_value: float
    data: List[List[float]] = field(default_factory=list)

    def sample(self, lat: float, lon: float) -> float:
        """Sample the elevation at (lat, lon) using nearest-cell lookup.

        Args:
            lat: Latitude of the query point.
            lon: Longitude of the query point.

        Returns:
            Elevation in meters at the nearest raster cell.

        Raises:
            DEMUnavailableError: If the point falls outside the fetched
                raster's bounds, or the cell has no data.
        """
        col = int((lon - self.xllcorner) / self.cellsize)
        row_from_bottom = int((lat - self.yllcorner) / self.cellsize)
        row = self.nrows - 1 - row_from_bottom

        if not (0 <= row < self.nrows) or not (0 <= col < self.ncols):
            raise DEMUnavailableError(f"Point ({lat}, {lon}) falls outside the fetched DEM raster bounds.")

        value = self.data[row][col]
        if value == self.nodata_value:
            raise DEMUnavailableError(f"Copernicus DEM has no data at ({lat}, {lon}) (NODATA cell).")
        return value


_AAIGRID_HEADER_KEYS = {
    "ncols",
    "nrows",
    "xllcorner",
    "yllcorner",
    "xllcenter",
    "yllcenter",
    "cellsize",
    "nodata_value",
}


def _parse_aaigrid(text: str) -> _RasterGrid:
    """Parse an ESRI ASCII Grid (AAIGrid) response body into a `_RasterGrid`.

    Args:
        text: Raw AAIGrid text (6 header lines followed by row data).

    Returns:
        Parsed `_RasterGrid`.

    Raises:
        DEMUnavailableError: If the text cannot be parsed as AAIGrid.
    """
    lines = text.strip().splitlines()
    header: Dict[str, float] = {}
    data_start = None
    for i, line in enumerate(lines):
        parts = line.split()
        if len(parts) == 2 and parts[0].lower() in _AAIGRID_HEADER_KEYS:
            try:
                header[parts[0].lower()] = float(parts[1])
            except ValueError as exc:
                raise DEMUnavailableError(f"Invalid AAIGrid header value on line: {line!r}") from exc
        else:
            data_start = i
            break

    if data_start is None or not header:
        raise DEMUnavailableError(
            "Could not parse AAIGrid header from Copernicus DEM response "
            f"(got {len(text)} chars, first 200: {text[:200]!r})."
        )

    try:
        ncols = int(header["ncols"])
        nrows = int(header["nrows"])
        cellsize = header["cellsize"]
        xll = header.get("xllcorner", header.get("xllcenter"))
        yll = header.get("yllcorner", header.get("yllcenter"))
        nodata = header.get("nodata_value", -9999.0)
    except KeyError as exc:
        raise DEMUnavailableError(f"AAIGrid header missing required field: {exc}") from exc

    if xll is None or yll is None:
        raise DEMUnavailableError("AAIGrid header missing corner/center coordinates.")

    data: List[List[float]] = []
    for line in lines[data_start:]:
        if not line.strip():
            continue
        try:
            data.append([float(v) for v in line.split()])
        except ValueError as exc:
            raise DEMUnavailableError(f"Invalid AAIGrid data row: {line[:100]!r}") from exc

    if len(data) != nrows:
        raise DEMUnavailableError(f"AAIGrid data has {len(data)} rows, header declared {nrows}.")

    return _RasterGrid(
        ncols=ncols, nrows=nrows, xllcorner=xll, yllcorner=yll, cellsize=cellsize, nodata_value=nodata, data=data
    )


class CopernicusDEMClient:
    """Client for fetching real Copernicus DEM GLO-30 elevation data.

    Fetches a single raster covering the bounding box of the requested
    points (one HTTP call per batch of points, rather than a per-point
    or per-N-points call), then samples each point from that raster.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = OPENTOPOGRAPHY_ENDPOINT,
        session: Optional[requests.Session] = None,
        bbox_margin_deg: float = DEFAULT_BBOX_MARGIN_DEG,
    ):
        """Initialize the client.

        Args:
            api_key: OpenTopography API key. Defaults to the
                OPENTOPOGRAPHY_API_KEY environment variable.
            endpoint: OpenTopography Global DEM API endpoint.
            session: Optional pre-configured requests.Session (useful for testing).
            bbox_margin_deg: Extra margin (decimal degrees) added around
                the requested points' bounding box when fetching the raster,
                to guard against edge-of-raster sampling issues.
        """
        self.api_key = api_key or os.environ.get("OPENTOPOGRAPHY_API_KEY")
        self.endpoint = endpoint
        self.session = session or requests.Session()
        self.bbox_margin_deg = bbox_margin_deg

    def fetch_elevation_raster(self, south: float, north: float, west: float, east: float, timeout: float = 60.0) -> _RasterGrid:
        """Fetch a Copernicus DEM raster covering the given bounding box.

        Args:
            south: Southern latitude bound.
            north: Northern latitude bound.
            west: Western longitude bound.
            east: Eastern longitude bound.
            timeout: Request timeout in seconds.

        Returns:
            Parsed `_RasterGrid` covering the requested bounding box.

        Raises:
            DEMUnavailableError: If no API key is configured, the request
                fails, or the response cannot be parsed.
        """
        if not self.api_key:
            raise DEMUnavailableError(
                "OPENTOPOGRAPHY_API_KEY is not set. Register a free API key at "
                "https://portal.opentopography.org/myopentopo and set it as an "
                "environment variable to fetch real Copernicus DEM data."
            )

        params = {
            "demtype": DEM_DATASET,
            "south": south,
            "north": north,
            "west": west,
            "east": east,
            "outputFormat": DEM_OUTPUT_FORMAT,
            "API_Key": self.api_key,
        }
        try:
            response = self.session.get(self.endpoint, params=params, timeout=timeout)
            response.raise_for_status()
        except requests.HTTPError as exc:
            body = exc.response.text[:500] if exc.response is not None else ""
            raise DEMUnavailableError(f"OpenTopography COP30 request failed: {exc}. Response body: {body!r}") from exc
        except requests.RequestException as exc:
            raise DEMUnavailableError(f"Failed to reach OpenTopography service: {exc}") from exc

        return _parse_aaigrid(response.text)

    def fetch_point_elevations(self, points: List[Tuple[float, float]], timeout: float = 60.0) -> List[float]:
        """Fetch elevation values for a batch of (lat, lon) points.

        Fetches a single raster covering the bounding box of all requested
        points (padded by `bbox_margin_deg`), then samples each point from
        it — one HTTP call regardless of point count, avoiding any
        per-request location-count limit.

        Args:
            points: List of (latitude, longitude) tuples.
            timeout: Request timeout in seconds for the raster fetch.

        Returns:
            List of elevations in meters, in the same order as `points`.

        Raises:
            DEMUnavailableError: If the raster cannot be fetched/parsed, or
                any point falls outside the fetched raster / has no data.
        """
        if not points:
            return []

        lats = [p[0] for p in points]
        lons = [p[1] for p in points]
        margin = self.bbox_margin_deg
        south, north = min(lats) - margin, max(lats) + margin
        west, east = min(lons) - margin, max(lons) + margin

        raster = self.fetch_elevation_raster(south, north, west, east, timeout=timeout)
        return [raster.sample(lat, lon) for lat, lon in points]

    @staticmethod
    def metadata() -> DEMAcquisitionMetadata:
        """Return provenance/acquisition metadata for the DEM source."""
        return DEMAcquisitionMetadata(
            source="Copernicus DEM GLO-30 via OpenTopography Global DEM API (demtype=COP30)",
            dataset=DEM_DATASET,
            resolution_m=DEM_RESOLUTION_M,
            crs=DEM_CRS,
            acquisition_note=(
                "Static elevation product derived from TanDEM-X radar acquisitions "
                "(~2011-2015), released 2021-2022. No 0-6h refresh cycle exists. "
                "Use for static elevation/slope only, never as a dynamic hydrology source."
            ),
        )
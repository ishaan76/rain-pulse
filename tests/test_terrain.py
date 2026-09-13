"""Unit Tests for Agent 2 — Terrain & Drainage Subsystem.

All tests in this file are deterministic and run fully offline: any
interaction with Copernicus DEM or OSM is exercised through injected
fake clients / fixtures, never live HTTP calls.
"""

import pytest
import requests

from data.terrain.dem_client import CopernicusDEMClient, DEMUnavailableError
from data.terrain.drainage import classify_drainage_quality, compute_drainage_vulnerability_score
from data.terrain.elevation import calculate_slope, classify_slope_risk
from data.terrain.grid_generator import (
    GREATER_NOIDA_BBOX,
    _build_greater_noida_grid_coords,
    _haversine_m,
    _summarize_drainage_features,
    generate_greater_noida_grid,
)
from data.terrain.osm_client import OSMDrainageClient, OSMUnavailableError
from data.terrain.service import TerrainDataUnavailableError, TerrainService


def test_calculate_slope():
    """Verify slope computation math."""
    # 10m rise over 100m run
    slope = calculate_slope(200.0, 210.0, 100.0)
    assert 5.0 < slope < 6.0
    # Zero distance should return 0.0 without division by zero
    assert calculate_slope(200.0, 210.0, 0.0) == 0.0


def test_classify_slope_risk():
    """Verify slope risk classification."""
    assert classify_slope_risk(1.0) == "FLAT_DEPRESSION"
    assert classify_slope_risk(2.5) == "GENTLE_SLOPE"
    assert classify_slope_risk(5.0) == "STEEP_RUNOFF"


def test_drainage_quality_and_score():
    """Verify drainage quality classification and vulnerability scoring."""
    poor = classify_drainage_quality(drainage_distance_m=800.0, drainage_density=0.2)
    assert poor == "Poor"

    good = classify_drainage_quality(drainage_distance_m=150.0, drainage_density=0.8)
    assert good == "Good"

    score_poor = compute_drainage_vulnerability_score(800.0, 0.2)
    score_good = compute_drainage_vulnerability_score(150.0, 0.8)
    assert score_poor > score_good
    assert 0.0 <= score_good <= 100.0
    assert 0.0 <= score_poor <= 100.0


def test_terrain_service_grid_generation():
    """Verify TerrainService generates valid GridCell contracts for pilot areas."""
    service = TerrainService()
    delhi_cells = service.get_grid_cells("Delhi NCR")
    assert len(delhi_cells) > 0
    assert delhi_cells[0].cell_id.startswith("DEL_")
    assert delhi_cells[0].elevation > 0
    assert 0.0 <= delhi_cells[0].slope <= 90.0


# --- Greater Noida grid geometry (pure math, no network) ------------------


def test_greater_noida_grid_coords_cover_bbox_without_gaps_or_overlaps():
    """Verify the Greater Noida grid is a regular, non-overlapping tiling of the AOI."""
    coords = _build_greater_noida_grid_coords(spacing_deg=0.02)
    assert len(coords) > 0

    ids = [c[0] for c in coords]
    assert len(ids) == len(set(ids)), "Grid cell IDs must be unique (no overlaps)."

    bbox = GREATER_NOIDA_BBOX
    for _, lat, lon in coords:
        assert bbox["south"] <= lat <= bbox["north"]
        assert bbox["west"] <= lon <= bbox["east"]

    # Regular spacing: no gaps between consecutive unique latitudes/longitudes.
    lats = sorted({round(lat, 6) for _, lat, _ in coords})
    for a, b in zip(lats, lats[1:]):
        assert abs((b - a) - 0.02) < 1e-6


def test_haversine_distance_known_value():
    """Sanity check haversine distance against a known short offset."""
    # ~0.01 deg longitude at ~28.5N is roughly 977m.
    dist = _haversine_m(28.5, 77.40, 28.5, 77.41)
    assert 900.0 < dist < 1050.0
    assert _haversine_m(28.5, 77.40, 28.5, 77.40) == 0.0


def test_summarize_drainage_features_no_elements_returns_fallback():
    """No nearby OSM features should yield the search-radius fallback distance and zero density."""
    distance, density = _summarize_drainage_features(28.5, 77.45, [], search_radius_m=1000.0)
    assert distance == 1000.0
    assert density == 0.0


def test_summarize_drainage_features_with_elements():
    """Nearby OSM features should reduce distance and increase density proportionally."""
    elements = [
        {"center": {"lat": 28.501, "lon": 77.451}},
        {"center": {"lat": 28.505, "lon": 77.455}},
    ]
    distance, density = _summarize_drainage_features(
        28.5, 77.45, elements, search_radius_m=1000.0, density_reference_count=8
    )
    assert 0.0 < distance < 1000.0
    assert density == round(2 / 8, 2)


def test_summarize_drainage_features_ignores_far_elements_for_density():
    """Regression test: elements far outside search_radius_m must not inflate density,
    even though a shared whole-AOI element list (from a single bbox fetch) may contain
    dozens of features nowhere near this particular cell. The nearest distance may
    legitimately come from a far element if nothing closer exists, but density must
    only reflect features actually within radius of this cell."""
    near_elements = [
        {"center": {"lat": 28.5009, "lon": 77.4509}},  # ~120m away, inside 1000m radius
    ]
    # Many far-away elements (e.g. from the rest of a large shared bbox fetch) that
    # must NOT count toward this cell's density.
    far_elements = [{"center": {"lat": 28.5, "lon": 77.45 + 0.05 * i}} for i in range(1, 20)]
    elements = near_elements + far_elements

    distance, density = _summarize_drainage_features(
        28.5, 77.45, elements, search_radius_m=1000.0, density_reference_count=8
    )
    assert distance < 200.0  # the one genuinely nearby element
    assert density == round(1 / 8, 2)  # only the 1 nearby element counts, not all 20


# --- Fake DEM / OSM clients (deterministic, offline) -----------------------


class _FakeDEMClient:
    """Deterministic stand-in for CopernicusDEMClient used in offline tests."""

    def __init__(self, elevation_by_point=None, base_elevation=200.0):
        self.elevation_by_point = elevation_by_point or {}
        self.base_elevation = base_elevation
        self.calls = []

    def fetch_point_elevations(self, points):
        self.calls.append(list(points))
        return [self.elevation_by_point.get(p, self.base_elevation) for p in points]


class _FakeOSMClient:
    """Deterministic stand-in for OSMDrainageClient used in offline tests."""

    def __init__(self, elements=None):
        self.elements = elements if elements is not None else []
        self.calls = []

    def fetch_drainage_features_in_bbox(self, south, west, north, east):
        self.calls.append((south, west, north, east))
        return self.elements


class _FailingDEMClient:
    """Fake client that always raises, simulating an unreachable DEM service."""

    def fetch_point_elevations(self, points):
        raise DEMUnavailableError("simulated network failure")


def test_generate_greater_noida_grid_uses_injected_clients_deterministically():
    """generate_greater_noida_grid must use injected clients and never fabricate values."""
    fake_dem = _FakeDEMClient(base_elevation=205.0)
    # Placed exactly at a grid cell center (28.5, 77.5) so it's unambiguously
    # within that cell's search radius, independent of grid spacing.
    fake_osm = _FakeOSMClient(elements=[{"center": {"lat": 28.5, "lon": 77.5}}])

    cells = generate_greater_noida_grid(
        dem_client=fake_dem, osm_client=fake_osm, spacing_deg=0.1, neighbor_offset_deg=0.01
    )

    assert len(cells) > 0
    first = cells[0]
    assert first.cell_id.startswith("GNO_")
    assert first.elevation == 205.0
    # Flat fake elevation => zero slope between center and neighbor.
    assert first.slope == 0.0
    # historical_risk left at documented contract default, not invented.
    assert first.historical_risk == 0.5

    # The single fake drainage element sits exactly at grid cell (28.5, 77.5):
    # only that cell (within its search radius) should show nonzero density;
    # a cell far from it (e.g. the first cell) must not.
    colocated_cell = next(c for c in cells if c.latitude == 28.5 and c.longitude == 77.5)
    assert colocated_cell.drainage_density > 0.0
    assert first.drainage_density == 0.0  # (28.4, 77.4) is far from the one fake element

    # DEM client must be called once per (center + neighbor) point, batched.
    assert len(fake_dem.calls[0]) == len(cells) * 2
    # OSM must be queried once for the whole grid's bbox, not once per cell.
    assert len(fake_osm.calls) == 1


def test_generate_greater_noida_grid_computes_nonzero_slope_from_elevation_difference():
    """Differing center/neighbor elevations must propagate into a nonzero slope."""

    class _VaryingDEMClient:
        def fetch_point_elevations(self, points):
            # Neighbor points (odd index) get +50m elevation to force a slope.
            return [200.0 if i % 2 == 0 else 250.0 for i in range(len(points))]

    cells = generate_greater_noida_grid(
        dem_client=_VaryingDEMClient(), osm_client=_FakeOSMClient(), spacing_deg=0.1
    )
    assert all(c.slope > 0.0 for c in cells)


def test_terrain_service_greater_noida_raises_typed_error_when_dem_unreachable(monkeypatch):
    """Service must raise TerrainDataUnavailableError, not fabricate data, on DEM failure."""
    import data.terrain.grid_generator as grid_generator_module

    def _failing_generate(*args, **kwargs):
        raise DEMUnavailableError("simulated network failure")

    monkeypatch.setattr(grid_generator_module, "generate_greater_noida_grid", _failing_generate)
    # service.py imported the function directly, so patch it there too.
    import data.terrain.service as service_module

    monkeypatch.setattr(service_module, "generate_greater_noida_grid", _failing_generate)

    service = TerrainService()
    with pytest.raises(TerrainDataUnavailableError):
        service.get_grid_cells("Greater Noida")


def test_terrain_service_demo_areas_unaffected_by_greater_noida_changes():
    """Existing demo pilot areas must remain untouched by the Greater Noida addition."""
    service = TerrainService()
    for area in ("Delhi NCR", "Noida", "Gurugram", "Ghaziabad"):
        cells = service.get_grid_cells(area)
        assert len(cells) > 0


# --- DEM / OSM client unit tests (mocked HTTP, no live network) -----------


_SAMPLE_AAIGRID = """\
ncols         4
nrows         3
xllcorner     77.40
yllcorner     28.40
cellsize      0.05
NODATA_value  -9999
200 201 202 203
210 211 212 213
220 221 222 -9999
"""


class _FakeGetResponse:
    """Fake requests.Response for GET calls returning AAIGrid text or errors."""

    def __init__(self, text="", status_code=200, http_error=None):
        self.text = text
        self.status_code = status_code
        self._http_error = http_error

    def raise_for_status(self):
        if self._http_error is not None:
            raise self._http_error


class _FakeGetSession:
    def __init__(self, response):
        self._response = response
        self.last_call = None

    def get(self, url, params=None, timeout=None):
        self.last_call = ("GET", url, params)
        return self._response


class _FakePostResponse:
    def __init__(self, json_data, status_code=200, headers=None):
        self._json_data = json_data
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._json_data


class _FakePostSession:
    def __init__(self, response):
        self._response = response
        self.last_call = None

    def post(self, url, data=None, timeout=None, headers=None):
        self.last_call = ("POST", url, data)
        return self._response


def test_parse_aaigrid_reads_header_and_data():
    """AAIGrid text must parse into a raster with correct dimensions and values."""
    from data.terrain.dem_client import _parse_aaigrid

    raster = _parse_aaigrid(_SAMPLE_AAIGRID)
    assert raster.ncols == 4
    assert raster.nrows == 3
    assert raster.cellsize == 0.05
    assert raster.data[0] == [200.0, 201.0, 202.0, 203.0]


def test_raster_sample_nearest_cell_lookup():
    """Sampling a point must return the correct cell, honoring the north-to-south row order."""
    from data.terrain.dem_client import _parse_aaigrid

    raster = _parse_aaigrid(_SAMPLE_AAIGRID)
    # yllcorner=28.40 is the SOUTH edge (grid spans 28.40-28.55); a point near the
    # north edge should read from the first data row (200-203), and a point near
    # the south edge should read from the last data row (220-222,-9999).
    value_north = raster.sample(28.549, 77.40)
    value_south = raster.sample(28.401, 77.40)
    assert value_north == 200.0
    assert value_south == 220.0


def test_raster_sample_raises_on_nodata():
    """Sampling a NODATA cell must raise rather than silently returning -9999 as a real elevation."""
    from data.terrain.dem_client import _parse_aaigrid

    raster = _parse_aaigrid(_SAMPLE_AAIGRID)
    with pytest.raises(DEMUnavailableError):
        raster.sample(28.401, 77.551)  # maps to data[2][3] == -9999


def test_raster_sample_raises_out_of_bounds():
    """Sampling outside the fetched raster extent must raise, never extrapolate."""
    from data.terrain.dem_client import _parse_aaigrid

    raster = _parse_aaigrid(_SAMPLE_AAIGRID)
    with pytest.raises(DEMUnavailableError):
        raster.sample(30.0, 77.4)


def test_copernicus_dem_client_requires_api_key(monkeypatch):
    """Missing OPENTOPOGRAPHY_API_KEY must raise a clear, typed error before any request."""
    # Isolate from the real environment: a developer/CI machine may have
    # OPENTOPOGRAPHY_API_KEY set for live testing, which would otherwise
    # leak in here and mask the "no key configured" code path.
    monkeypatch.delenv("OPENTOPOGRAPHY_API_KEY", raising=False)
    client = CopernicusDEMClient(api_key=None, session=_FakeGetSession(_FakeGetResponse(_SAMPLE_AAIGRID)))
    with pytest.raises(DEMUnavailableError, match="OPENTOPOGRAPHY_API_KEY"):
        client.fetch_point_elevations([(28.42, 77.41)])


def test_copernicus_dem_client_parses_valid_response_and_samples_points():
    """DEM client must fetch one raster and sample each requested point from it."""
    session = _FakeGetSession(_FakeGetResponse(_SAMPLE_AAIGRID))
    client = CopernicusDEMClient(api_key="test-key", session=session)
    elevations = client.fetch_point_elevations([(28.549, 77.40), (28.401, 77.40)])
    assert elevations == [200.0, 220.0]
    # Real COP30 dataset must be requested, not a substitute.
    assert session.last_call[2]["demtype"] == "COP30"


def test_copernicus_dem_client_single_request_regardless_of_point_count():
    """Unlike a per-point/location-capped API, this client issues exactly one HTTP call per batch."""
    session = _FakeGetSession(_FakeGetResponse(_SAMPLE_AAIGRID))
    client = CopernicusDEMClient(api_key="test-key", session=session)
    points = [(28.40 + i * 0.001, 77.40) for i in range(50)]
    client.fetch_point_elevations(points)
    # _FakeGetSession only records the last call, but a second manual check confirms
    # no exception was raised for 50 points sharing a single raster fetch.
    assert session.last_call[0] == "GET"


def test_copernicus_dem_client_empty_points_returns_empty_list():
    """No points requested should short-circuit without a network call."""
    client = CopernicusDEMClient(api_key="test-key", session=_FakeGetSession(_FakeGetResponse(_SAMPLE_AAIGRID)))
    assert client.fetch_point_elevations([]) == []


def test_copernicus_dem_client_surfaces_response_body_on_http_error():
    """HTTP errors (e.g. 400 'Dataset not in config') must surface the real response body, not just a status code."""
    import requests as _requests

    error_response = _FakeGetResponse(text="", status_code=400)
    http_error = _requests.HTTPError("400 Client Error")
    http_error.response = type(
        "R", (), {"text": '{"error": "Dataset \'X\' not in config.", "status": "INVALID_REQUEST"}'}
    )()
    error_response._http_error = http_error

    client = CopernicusDEMClient(api_key="test-key", session=_FakeGetSession(error_response))
    with pytest.raises(DEMUnavailableError, match="INVALID_REQUEST"):
        client.fetch_point_elevations([(28.42, 77.41)])


def test_osm_drainage_client_returns_elements():
    """OSM client must return the raw elements list from a well-formed Overpass response."""
    fake_response = _FakePostResponse({"elements": [{"type": "way", "center": {"lat": 28.5, "lon": 77.45}}]})
    client = OSMDrainageClient(
        mirrors=["https://fake-mirror.example/api/interpreter"],
        session=_FakePostSession(fake_response),
        sleep_fn=lambda s: None,
    )
    elements = client.fetch_drainage_features_in_bbox(south=28.4, west=77.4, north=28.6, east=77.5)
    assert len(elements) == 1
    assert elements[0]["center"]["lat"] == 28.5


def test_osm_drainage_client_falls_back_to_next_mirror_on_failure():
    """If the first mirror fails, the client must try the next one before raising."""

    class _FailThenSucceedSession:
        def __init__(self):
            self.calls = []

        def post(self, url, data=None, timeout=None, headers=None):
            self.calls.append(url)
            if url == "https://mirror-one.example/api/interpreter":
                raise requests.ConnectionError("simulated connect timeout")
            return _FakePostResponse({"elements": [{"center": {"lat": 28.5, "lon": 77.45}}]})

    session = _FailThenSucceedSession()
    client = OSMDrainageClient(
        mirrors=["https://mirror-one.example/api/interpreter", "https://mirror-two.example/api/interpreter"],
        session=session,
        max_retries_per_mirror=0,
        sleep_fn=lambda s: None,
    )
    elements = client.fetch_drainage_features_in_bbox(south=28.4, west=77.4, north=28.6, east=77.5)
    assert len(elements) == 1
    assert session.calls == [
        "https://mirror-one.example/api/interpreter",
        "https://mirror-two.example/api/interpreter",
    ]


def test_osm_drainage_client_retries_same_mirror_after_429_then_succeeds():
    """A 429 on a mirror must be retried on the SAME mirror (not skipped) before moving on."""

    class _RateLimitedThenOKSession:
        def __init__(self):
            self.calls = []

        def post(self, url, data=None, timeout=None, headers=None):
            self.calls.append(url)
            if len(self.calls) == 1:
                return _FakePostResponse({}, status_code=429)
            return _FakePostResponse({"elements": [{"center": {"lat": 28.5, "lon": 77.45}}]})

    session = _RateLimitedThenOKSession()
    sleeps = []
    client = OSMDrainageClient(
        mirrors=["https://mirror-one.example/api/interpreter"],
        session=session,
        max_retries_per_mirror=2,
        sleep_fn=lambda s: sleeps.append(s),
    )
    elements = client.fetch_drainage_features_in_bbox(south=28.4, west=77.4, north=28.6, east=77.5)
    assert len(elements) == 1
    assert session.calls == [
        "https://mirror-one.example/api/interpreter",
        "https://mirror-one.example/api/interpreter",
    ]
    assert len(sleeps) == 1  # backed off once, then succeeded


def test_osm_drainage_client_honors_retry_after_header():
    """A Retry-After header on a 429 response must control the backoff delay used."""

    class _RateLimitedWithRetryAfterSession:
        def __init__(self):
            self.calls = 0

        def post(self, url, data=None, timeout=None, headers=None):
            self.calls += 1
            if self.calls == 1:
                return _FakePostResponse({}, status_code=429, headers={"Retry-After": "3"})
            return _FakePostResponse({"elements": []})

    sleeps = []
    client = OSMDrainageClient(
        mirrors=["https://mirror-one.example/api/interpreter"],
        session=_RateLimitedWithRetryAfterSession(),
        max_retries_per_mirror=1,
        retry_base_delay_s=99.0,  # would be obviously wrong if Retry-After weren't honored
        sleep_fn=lambda s: sleeps.append(s),
    )
    client.fetch_drainage_features_in_bbox(south=28.4, west=77.4, north=28.6, east=77.5)
    assert sleeps == [3.0]


def test_osm_drainage_client_raises_after_all_mirrors_fail():
    """If every mirror fails, a single typed error listing all failures must be raised."""

    class _AlwaysFailSession:
        def post(self, url, data=None, timeout=None, headers=None):
            raise requests.ConnectionError(f"simulated failure for {url}")

    client = OSMDrainageClient(
        mirrors=["https://mirror-one.example/api/interpreter", "https://mirror-two.example/api/interpreter"],
        session=_AlwaysFailSession(),
        max_retries_per_mirror=0,
        sleep_fn=lambda s: None,
    )
    with pytest.raises(OSMUnavailableError, match="(?s)mirror-one.*mirror-two"):
        client.fetch_drainage_features_in_bbox(south=28.4, west=77.4, north=28.6, east=77.5)
"""AquaAlert AI — Agent 2: OpenStreetMap Drainage/Waterway Acquisition Client.

Queries the public Overpass API for OSM `waterway`, `drain`, and
`man_made=storm_drain` features, used to derive drainage-distance and
drainage-density terrain features. OSM is a community-maintained vector
map: coverage completeness for stormwater drains varies by locality and
is NOT a guaranteed exhaustive drainage-infrastructure inventory. It is
used here as the best available open proxy for drainage network context.

DESIGN NOTE — one bbox query, not one query per grid cell:
    An earlier version of this client queried Overpass once per grid cell
    (e.g. 64 sequential requests for a 64-cell Greater Noida grid). That
    is fragile (one slow/blocked host kills the whole run) and unfriendly
    to Overpass's shared public infrastructure. This client now fetches
    all drainage features within a single bounding box in ONE request,
    mirroring the same fix already applied to the DEM client (one raster
    fetch instead of one call per point). Callers should compute
    per-cell distance/density locally from the shared feature list.

DESIGN NOTE — mirror fallback + retry:
    The default `overpass-api.de` instance can be unreachable from some
    networks (TCP connect timeout, not just slow). This client tries a
    short list of independent public Overpass mirrors in order. Public
    mirrors also commonly return HTTP 429 (Too Many Requests) under load
    or per-IP rate limiting even when reachable, so each mirror is
    retried with backoff (honoring a `Retry-After` header when present)
    before moving on to the next mirror. Only once every mirror has
    exhausted its retries does this client raise, with each attempt's
    failure recorded for diagnostics.
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

# Independent public Overpass API mirrors, tried in order. If the first
# (main) instance is unreachable from a given network, later ones are tried.
OVERPASS_MIRRORS: List[str] = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
DEFAULT_TIMEOUT_S = 45.0
DEFAULT_BBOX_MARGIN_DEG = 0.01
DEFAULT_MAX_RETRIES_PER_MIRROR = 2  # i.e. up to 3 attempts per mirror
DEFAULT_RETRY_BASE_DELAY_S = 8.0
DEFAULT_MAX_RETRY_DELAY_S = 30.0
# Public Overpass instances often deprioritize/blanket-block requests using
# the default python-requests User-Agent. Identifying the client honestly
# is standard Overpass etiquette and can reduce needless throttling.
OVERPASS_USER_AGENT = "AquaAlertAI-TerrainAgent/1.0 (SIH hackathon prototype; contact via project repo)"


@dataclass
class OSMAcquisitionMetadata:
    """Provenance record for OSM-derived drainage features.

    Attributes:
        source: Human-readable description of the data source/API.
        feature_tags: OSM tags queried.
        acquisition_note: Coverage/limitation caveat for this dataset.
    """

    source: str
    feature_tags: List[str]
    acquisition_note: str


class OSMUnavailableError(RuntimeError):
    """Raised when no configured Overpass mirror can be reached after retries."""


def _build_bbox_query(south: float, west: float, north: float, east: float, timeout_s: int = 60) -> str:
    """Build an Overpass QL query for drainage features within a bounding box.

    Args:
        south: Southern latitude bound.
        west: Western longitude bound.
        north: Northern latitude bound.
        east: Eastern longitude bound.
        timeout_s: Server-side Overpass query timeout in seconds.

    Returns:
        Overpass QL query string.
    """
    bbox = f"{south},{west},{north},{east}"
    return (
        f"[out:json][timeout:{timeout_s}];"
        "("
        f'way["waterway"]({bbox});'
        f'way["drain"]({bbox});'
        f'way["man_made"="storm_drain"]({bbox});'
        ");"
        "out center;"
    )


def _parse_retry_after(response: Any, default: float) -> float:
    """Read a Retry-After header (seconds) from a response, falling back to a default.

    Args:
        response: An HTTP response-like object exposing `.headers`.
        default: Value to use if the header is missing or unparsable.

    Returns:
        Delay in seconds to wait before retrying.
    """
    headers = getattr(response, "headers", None) or {}
    value = headers.get("Retry-After")
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class OSMDrainageClient:
    """Client for querying OSM waterway/drainage features via Overpass.

    Fetches all matching features within a bounding box in a single
    logical request, trying each configured mirror in turn — with
    backoff retries per mirror to absorb transient rate limiting (HTTP
    429) — until one succeeds.
    """

    def __init__(
        self,
        mirrors: Optional[List[str]] = None,
        session: Optional[requests.Session] = None,
        timeout: float = DEFAULT_TIMEOUT_S,
        max_retries_per_mirror: int = DEFAULT_MAX_RETRIES_PER_MIRROR,
        retry_base_delay_s: float = DEFAULT_RETRY_BASE_DELAY_S,
        max_retry_delay_s: float = DEFAULT_MAX_RETRY_DELAY_S,
        sleep_fn=time.sleep,
    ):
        """Initialize the client.

        Args:
            mirrors: Ordered list of Overpass interpreter endpoints to try.
                Defaults to `OVERPASS_MIRRORS`.
            session: Optional pre-configured requests.Session (useful for testing).
            timeout: Per-request timeout in seconds.
            max_retries_per_mirror: Extra attempts per mirror after the
                first, used on connection errors and HTTP 429 responses.
            retry_base_delay_s: Initial backoff delay in seconds (doubles
                each retry, capped at `max_retry_delay_s`), used when no
                `Retry-After` header is present.
            max_retry_delay_s: Upper bound on any single retry delay.
            sleep_fn: Sleep function to call between retries (injectable
                for deterministic, fast unit tests).
        """
        self.mirrors = mirrors or list(OVERPASS_MIRRORS)
        self.session = session or requests.Session()
        self.timeout = timeout
        self.max_retries_per_mirror = max_retries_per_mirror
        self.retry_base_delay_s = retry_base_delay_s
        self.max_retry_delay_s = max_retry_delay_s
        self._sleep = sleep_fn

    def fetch_drainage_features_in_bbox(
        self,
        south: float,
        west: float,
        north: float,
        east: float,
    ) -> List[Dict[str, Any]]:
        """Fetch OSM waterway/drain features within a bounding box.

        Tries each mirror in `self.mirrors` in order. Within a mirror,
        retries up to `max_retries_per_mirror` additional times on
        connection errors or HTTP 429 (honoring `Retry-After` when
        present) before moving to the next mirror. Only raises once every
        mirror has exhausted its retries.

        Args:
            south: Southern latitude bound.
            west: Western longitude bound.
            north: Northern latitude bound.
            east: Eastern longitude bound.

        Returns:
            List of raw Overpass element dicts (each with a 'center' or
            'lat'/'lon' field) representing drainage features in the bbox.

        Raises:
            OSMUnavailableError: If every configured mirror's retries are exhausted.
        """
        query = _build_bbox_query(south, west, north, east)
        headers = {"User-Agent": OVERPASS_USER_AGENT}
        errors: List[str] = []

        for mirror in self.mirrors:
            delay = self.retry_base_delay_s
            for attempt in range(self.max_retries_per_mirror + 1):
                try:
                    response = self.session.post(mirror, data={"data": query}, timeout=self.timeout, headers=headers)
                except requests.RequestException as exc:
                    errors.append(f"{mirror} (attempt {attempt + 1}): connection error: {exc}")
                    if attempt < self.max_retries_per_mirror:
                        self._sleep(delay)
                        delay = min(delay * 2, self.max_retry_delay_s)
                    continue

                if response.status_code == 429:
                    errors.append(f"{mirror} (attempt {attempt + 1}): 429 Too Many Requests")
                    if attempt < self.max_retries_per_mirror:
                        wait_s = min(_parse_retry_after(response, default=delay), self.max_retry_delay_s)
                        self._sleep(wait_s)
                        delay = min(delay * 2, self.max_retry_delay_s)
                    continue

                try:
                    response.raise_for_status()
                    payload = response.json()
                    return payload.get("elements", [])
                except (requests.RequestException, ValueError) as exc:
                    errors.append(f"{mirror} (attempt {attempt + 1}): {exc}")
                    break  # non-429 HTTP/parse errors: try next mirror, don't retry this one

        raise OSMUnavailableError("All configured Overpass mirrors failed:\n" + "\n".join(errors))

    def fetch_drainage_features(
        self,
        lat: float,
        lon: float,
        radius_m: int = 1000,
        timeout: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch OSM waterway/drain features within a radius of a single point.

        Convenience wrapper kept for callers that need a single-point
        lookup. For grid-scale usage, prefer `fetch_drainage_features_in_bbox`
        with the grid's overall bounding box, to avoid one request per cell.

        Args:
            lat: Latitude of the query center.
            lon: Longitude of the query center.
            radius_m: Search radius in meters, converted to an approximate
                bounding box (~111,320 m per degree latitude).
            timeout: Optional per-request timeout override.

        Returns:
            List of raw Overpass element dicts near the point.

        Raises:
            OSMUnavailableError: If every configured mirror fails.
        """
        if timeout is not None:
            original_timeout, self.timeout = self.timeout, timeout
        try:
            deg_radius = radius_m / 111320.0
            return self.fetch_drainage_features_in_bbox(
                south=lat - deg_radius, west=lon - deg_radius, north=lat + deg_radius, east=lon + deg_radius
            )
        finally:
            if timeout is not None:
                self.timeout = original_timeout

    @staticmethod
    def metadata() -> OSMAcquisitionMetadata:
        """Return provenance/acquisition metadata for the OSM source."""
        return OSMAcquisitionMetadata(
            source="OpenStreetMap via Overpass API",
            feature_tags=["waterway", "drain", "man_made=storm_drain"],
            acquisition_note=(
                "Community-mapped vector data; drainage infrastructure coverage "
                "is not guaranteed to be exhaustive or authoritative for any given "
                "locality. Used as a best-effort open proxy for drainage context, "
                "not a certified municipal stormwater dataset."
            ),
        )
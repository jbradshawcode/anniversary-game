"""Shared helpers for the place pipeline: env, http, paths, geometry."""
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple

def _find_repo_root(start: Path) -> Path:
    p = start.resolve()
    for parent in [p] + list(p.parents):
        if (parent / ".git").exists():
            return parent
    return p.parent


REPO_ROOT = _find_repo_root(Path(__file__))
REFS_ROOT = REPO_ROOT / "refs"


def load_api_key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not key:
        env = REPO_ROOT / ".env"
        if env.exists():
            for line in env.read_text().splitlines():
                if line.startswith("GOOGLE_MAPS_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    break
    if not key or key == "PASTE_YOUR_KEY_HERE":
        sys.exit("Set GOOGLE_MAPS_API_KEY in .env first.")
    return key


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return s or "place"


def place_dir(slug: str) -> Path:
    d = REFS_ROOT / slug
    d.mkdir(parents=True, exist_ok=True)
    return d


def http_json(url: str, retries: int = 3) -> Dict[str, Any]:
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "pygame-place-pipeline"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001 - network flake, retry
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("GET failed after %d tries: %s (%s)" % (retries, url, last))


def http_download(url: str, dest: Path, retries: int = 3) -> bool:
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "pygame-place-pipeline"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            if len(data) < 1024:  # an API error body, not an image
                last = "tiny response (%d bytes)" % len(data)
                continue
            dest.write_bytes(data)
            return True
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (attempt + 1))
    print("  !! download failed: %s (%s)" % (dest.name, last))
    return False


def qs(params: Dict[str, Any]) -> str:
    return urllib.parse.urlencode(params)


# ── geometry ──────────────────────────────────────────────────────────────────

def haversine_m(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    r = 6371000.0
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def point_in_ring(pt: Tuple[float, float], ring: List[Tuple[float, float]]) -> bool:
    # ray casting; pt and ring are (lat, lng)
    x, y = pt[1], pt[0]
    inside = False
    n = len(ring)
    for i in range(n):
        xi, yi = ring[i][1], ring[i][0]
        xj, yj = ring[i - 1][1], ring[i - 1][0]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-18) + xi):
            inside = not inside
    return inside


def ring_centroid(ring: List[Tuple[float, float]]) -> Tuple[float, float]:
    n = len(ring)
    return (sum(p[0] for p in ring) / n, sum(p[1] for p in ring) / n)


def footprint_dimensions_m(ring: List[Tuple[float, float]]) -> Dict[str, float]:
    """Real-world dimensions of the footprint.

    Reports BOTH the axis-aligned E-W/N-S box AND the oriented (minimum-area)
    rectangle. Buildings are rarely aligned to the compass, so the axis-aligned box
    over-states size and the wrong axis reads as "long" — use the oriented values
    (long_m/short_m + long_axis_bearing) for shape and to seat the compass frame.
    """
    lats = [p[0] for p in ring]
    lngs = [p[1] for p in ring]
    south, north = min(lats), max(lats)
    west, east = min(lngs), max(lngs)
    mid_lat = (south + north) / 2
    width_m = haversine_m((mid_lat, west), (mid_lat, east))
    depth_m = haversine_m((south, (west + east) / 2), (north, (west + east) / 2))
    oriented = _min_area_rect_m(ring, mid_lat)
    return {
        "bbox": {"south": south, "west": west, "north": north, "east": east},
        "width_m": round(width_m, 2),
        "depth_m": round(depth_m, 2),
        **oriented,
    }


def _project_m(ring: List[Tuple[float, float]], lat0: float) -> List[Tuple[float, float]]:
    """Equirectangular (lat,lng)->(east_m, north_m) about lat0 — local, good to ~km."""
    k = math.cos(math.radians(lat0))
    return [((lng) * 111320.0 * k, (lat) * 110540.0) for lat, lng in ring]


def _convex_hull(pts: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: List[Tuple[float, float]] = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper: List[Tuple[float, float]] = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _min_area_rect_m(ring: List[Tuple[float, float]], lat0: float) -> Dict[str, float]:
    """Minimum-area bounding rectangle of the footprint, in metres.

    Returns the long/short side lengths and the compass bearing of the long axis
    (0=N, 90=E). The optimal rectangle is collinear with one hull edge.
    """
    hull = _convex_hull(_project_m(ring, lat0))
    if len(hull) < 3:
        return {"long_m": 0.0, "short_m": 0.0, "long_axis_bearing": 0.0}
    best = None
    n = len(hull)
    for i in range(n):
        ax, ay = hull[i]
        bx, by = hull[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        elen = math.hypot(ex, ey) or 1e-9
        ux, uy = ex / elen, ey / elen          # edge unit (axis 1)
        vx, vy = -uy, ux                        # perpendicular (axis 2)
        us = [(px - ax) * ux + (py - ay) * uy for px, py in hull]
        vs = [(px - ax) * vx + (py - ay) * vy for px, py in hull]
        du, dv = max(us) - min(us), max(vs) - min(vs)
        area = du * dv
        if best is None or area < best[0]:
            best = (area, du, dv, ux, uy)
    _, du, dv, ux, uy = best
    if du >= dv:
        long_m, short_m, lx, ly = du, dv, ux, uy
    else:
        long_m, short_m, lx, ly = dv, du, -uy, ux
    bearing = (math.degrees(math.atan2(lx, ly)) + 360) % 360  # x=east, y=north
    return {
        "long_m": round(long_m, 2),
        "short_m": round(short_m, 2),
        "long_axis_bearing": round(bearing % 180, 1),
    }


def image_capture_date(path: Path) -> str:
    """Best-effort EXIF capture date 'YYYY-MM-DD'; '' if absent/stripped.

    Most web JPEGs have EXIF stripped, so treat a hit as a bonus, not a guarantee.
    """
    try:
        from PIL import Image  # local import: optional dependency
        exif = Image.open(path).getexif()
        raw = ""
        for ifd_key in (0x8769, None):  # Exif IFD, then top-level (DateTime)
            src = exif.get_ifd(ifd_key) if ifd_key else exif
            for tag in (36867, 36868, 306):  # Original, Digitized, DateTime
                if tag in src:
                    raw = str(src[tag])
                    break
            if raw:
                break
        if raw and ":" in raw:
            return raw.split(" ")[0].replace(":", "-")
    except Exception:  # noqa: BLE001 - EXIF parsing is best-effort
        pass
    return ""


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2))
    print("  -> %s" % path.relative_to(REPO_ROOT))

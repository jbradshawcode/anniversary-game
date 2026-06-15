"""Stage 0 — resolve a place to coordinates, footprint, aerial, and facade.

Online sources of truth only:
  - geocode .................. Google Geocoding API
  - building footprint ....... OpenStreetMap Overpass (real polygon)
  - aerial (satellite) ....... Google Static Maps
  - facade + capture date .... Google Street View Static (+ metadata)

Writes refs/<slug>/manifest.json and refs/<slug>/_resolve/*.{jpg,png}.

Run:
  python3 $SK/resolve.py "The Salutation" \
      --address "154 King Street, Hammersmith, London W6 0QU"
"""
import argparse
import datetime
import math
import urllib.parse
from typing import Dict, List, Optional, Tuple

from common import (  # type: ignore
    REPO_ROOT, http_download, http_json, load_api_key, place_dir, qs,
    footprint_dimensions_m, haversine_m, point_in_ring, ring_centroid,
    slugify, write_json,
)

OVERPASS = "https://overpass-api.de/api/interpreter?data="
GEOCODE = "https://maps.googleapis.com/maps/api/geocode/json?"
STATICMAP = "https://maps.googleapis.com/maps/api/staticmap?"
SV_IMG = "https://maps.googleapis.com/maps/api/streetview?"
SV_META = "https://maps.googleapis.com/maps/api/streetview/metadata?"


def geocode(address: str, key: str) -> Tuple[float, float, str]:
    data = http_json(GEOCODE + qs({"address": address, "key": key}))
    if data.get("status") != "OK":
        raise RuntimeError("geocode failed: %s" % data.get("status"))
    top = data["results"][0]
    loc = top["geometry"]["location"]
    return loc["lat"], loc["lng"], top["formatted_address"]


def building_footprint(lat: float, lng: float) -> Optional[Dict]:
    q = "[out:json][timeout:25];way(around:45,%f,%f)[\"building\"];out geom;" % (lat, lng)
    data = http_json(OVERPASS + urllib.parse.quote(q))
    rings: List[Tuple[dict, List[Tuple[float, float]]]] = []
    for el in data.get("elements", []):
        geom = el.get("geometry")
        if not geom:
            continue
        ring = [(g["lat"], g["lon"]) for g in geom]
        rings.append((el, ring))
    if not rings:
        return None
    pt = (lat, lng)
    containing = [(el, r) for el, r in rings if point_in_ring(pt, r)]
    if containing:
        el, ring = containing[0]
    else:  # nearest centroid
        el, ring = min(rings, key=lambda er: haversine_m(pt, ring_centroid(er[1])))
    dims = footprint_dimensions_m(ring)
    return {
        "osm_id": el.get("id"),
        "osm_tags": el.get("tags", {}),
        "polygon": [[round(a, 7), round(b, 7)] for a, b in ring],
        "centroid": [round(c, 7) for c in ring_centroid(ring)],
        "contains_geocode_point": bool(containing),
        **dims,
    }


def bearing(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    lat1, lat2 = math.radians(a[0]), math.radians(b[0])
    dlon = math.radians(b[1] - a[1])
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def fetch_aerial(lat: float, lng: float, out_dir, key: str) -> List[Dict]:
    out = []
    for zoom in (19, 20):
        dest = out_dir / ("aerial_z%d.png" % zoom)
        url = STATICMAP + qs({
            "center": "%f,%f" % (lat, lng), "zoom": zoom,
            "size": "640x640", "scale": 2, "maptype": "satellite", "key": key,
        })
        if http_download(url, dest):
            out.append({"file": dest.name, "zoom": zoom, "type": "aerial"})
    return out


def fetch_facade(target: Tuple[float, float], out_dir, key: str) -> List[Dict]:
    """Find the nearest Street View pano and shoot it AT the building centroid."""
    meta = http_json(SV_META + qs({
        "location": "%f,%f" % target, "source": "outdoor", "key": key,
    }))
    if meta.get("status") != "OK":
        print("  !! street view metadata: %s" % meta.get("status"))
        return []
    cam = (meta["location"]["lat"], meta["location"]["lng"])
    head = bearing(cam, target)
    capture = meta.get("date", "unknown")
    print("  street view pano %s (%s), heading %.0f -> facade" % (meta.get("pano_id", "?")[:10], capture, head))
    out = []
    # wide fan of headings: the front door + any side carriage arch / garden passage
    # are usually OFF-centre on the facade — one centred shot misses them.
    for dh, label in [(0, "facade"), (-25, "facade_l"), (25, "facade_r"),
                      (-50, "facade_ll"), (50, "facade_rr")]:
        dest = out_dir / ("%s.jpg" % label)
        url = SV_IMG + qs({
            "size": "640x480", "location": "%f,%f" % cam,
            "heading": round((head + dh) % 360), "fov": 80, "pitch": 8,
            "source": "outdoor", "key": key,
        })
        if http_download(url, dest):
            out.append({"file": dest.name, "type": "facade",
                        "heading": round((head + dh) % 360), "capture_date": capture})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--address", required=True)
    args = ap.parse_args()

    key = load_api_key()
    slug = slugify(args.name)
    pdir = place_dir(slug)
    rdir = pdir / "_resolve"
    rdir.mkdir(exist_ok=True)

    print("Stage 0 — resolving %s" % args.name)
    lat, lng, formatted = geocode(args.address, key)
    print("  geocode: %.6f, %.6f  (%s)" % (lat, lng, formatted))

    fp = building_footprint(lat, lng)
    if fp:
        print("  footprint: OSM %s  axis-box %.1f x %.1f m" % (
            fp["osm_id"], fp["width_m"], fp["depth_m"]))
        print("  oriented:  long %.1f m x short %.1f m, long axis bears %.0f deg"
              " (contains point: %s)" % (
                  fp["long_m"], fp["short_m"], fp["long_axis_bearing"],
                  fp["contains_geocode_point"]))
    else:
        print("  !! no OSM building footprint found within 45 m")

    target = (fp["centroid"][0], fp["centroid"][1]) if fp else (lat, lng)
    aerial = fetch_aerial(target[0], target[1], rdir, key)
    facade = fetch_facade(target, rdir, key)

    sv_dates = sorted({f.get("capture_date") for f in facade if f.get("capture_date")})
    manifest = {
        "name": args.name,
        "slug": slug,
        "queried_address": args.address,
        "formatted_address": formatted,
        "resolved_at": datetime.date.today().isoformat(),
        "geocode": {"lat": round(lat, 7), "lng": round(lng, 7)},
        "footprint": fp,
        # currency: compare these dates against gallery capture dates (stage 1). A big
        # gap means the interior may have been refurbished since — see dirty-data.md.
        "currency": {"street_view": sv_dates, "aerial_approx": "see Google imagery date"},
        # interior360 + floorplan are filled in stage 1 via gather.py (they are SEARCHED
        # for, not API-fetchable): planning-portal drawings, estate-agent / CAMRA listings,
        # brewery site, Google "see inside" 360s.
        "evidence": {"aerial": aerial, "facade": facade, "floorplan": [],
                     "interior360": [], "interior": [], "exterior": []},
    }
    write_json(pdir / "manifest.json", manifest)
    print("Done. Evidence in %s" % rdir.relative_to(REPO_ROOT))
    print("NEXT (stage 1): search for a published FLOOR PLAN and INTERIOR 360s before")
    print("  the gallery — a real plan one-shots the shape. See SKILL.md Phase 1.")


if __name__ == "__main__":
    main()

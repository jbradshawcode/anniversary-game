"""Fetch Google Street View reference images along King Street, Hammersmith.

Covers Latymer Upper School (237) east to the Plough & Harrow / Wetherspoons (120).

Usage:
    1. Put your API key in .env:  GOOGLE_MAPS_API_KEY=AIza...
    2. Run:  python3 scripts/fetch_streetview.py
    3. Images saved to streetview_refs/
"""
import os
import sys
import urllib.request
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    print("Install python-dotenv:  pip install python-dotenv")
    sys.exit(1)

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
if not API_KEY or API_KEY == "PASTE_YOUR_KEY_HERE":
    print("Set GOOGLE_MAPS_API_KEY in .env first.")
    sys.exit(1)

# Latymer Upper School (237 King St) to the Plough & Harrow / Wetherspoons (120)
START_LAT, START_LNG = 51.49335, -0.24095
END_LAT, END_LNG = 51.49276, -0.23144
NUM_POINTS = 78

OUT_DIR = Path(__file__).resolve().parent.parent / "streetview_refs"
OUT_DIR.mkdir(exist_ok=True)

BASE_URL = (
    "https://maps.googleapis.com/maps/api/streetview"
    "?size=640x480&fov=80&pitch=5&source=outdoor"
    "&location={lat},{lng}&heading={heading}&key={key}"
)

points = []
for i in range(NUM_POINTS):
    t = i / max(NUM_POINTS - 1, 1)
    lat = START_LAT + t * (END_LAT - START_LAT)
    lng = START_LNG + t * (END_LNG - START_LNG)
    points.append((lat, lng))

fetched = 0
for idx, (lat, lng) in enumerate(points, start=1):
    print(f"Point {idx:02d}/{NUM_POINTS}  ({lat:.5f}, {lng:.5f})")

    for heading, label in [(350, "north"), (170, "south")]:
        url = BASE_URL.format(lat=lat, lng=lng, heading=heading, key=API_KEY)
        path = OUT_DIR / f"{idx:02d}_{label}.jpg"
        if path.exists():
            print(f"  -> {path.name} (cached)")
            fetched += 1
            continue
        try:
            urllib.request.urlretrieve(url, path)
            print(f"  -> {path.name}")
            fetched += 1
        except Exception as e:
            print(f"  !! {label} failed: {e}")

print(f"\nDone — {fetched} images in {OUT_DIR}")

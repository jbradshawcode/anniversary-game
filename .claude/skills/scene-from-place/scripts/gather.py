"""Stage 1 — download reference images (URLs harvested via MCP) with provenance.

URL harvesting from JS-rendered galleries / bot-blocked sites is done with the
Playwright MCP; this tool just downloads a vetted URL list and records where each
image came from + when it was captured, appending to the place manifest.

Run:
  python3 $SK/gather.py the_salutation --urls /tmp/sal_urls.txt \
      --source official-website --category gallery --captured 2024
"""
import argparse
import json
import re
from pathlib import Path

from common import REPO_ROOT, http_download, image_capture_date, place_dir, write_json  # type: ignore

# Provenance trust tiers — when photos disagree, the higher tier and the newer date win.
# See reference/dirty-data.md.
TRUST = {"official": 3, "estate-agent": 3, "camra": 2, "review": 2, "blog": 1, "unknown": 0}
BUCKETS = {"gallery": "interior", "interior": "interior", "floorplan": "floorplan",
           "interior360": "interior360", "exterior": "exterior"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--urls", required=True, help="text file, one URL per line")
    ap.add_argument("--source", required=True, help="provenance, e.g. official-website")
    ap.add_argument("--category", default="gallery", choices=sorted(BUCKETS),
                    help="subfolder under refs/<slug>/ (one of the known evidence buckets)")
    ap.add_argument("--captured", default="",
                    help="capture date/year (REQUIRED for dirty-data handling; EXIF is a fallback)")
    ap.add_argument("--trust", default="unknown",
                    help="provenance tier: official|estate-agent|camra|review|blog|unknown")
    args = ap.parse_args()

    if args.trust not in TRUST:
        print("  !! unknown --trust %r; treating as 'unknown' (tier 0)" % args.trust)

    pdir = place_dir(args.slug)
    out = pdir / args.category
    out.mkdir(exist_ok=True)
    urls = [u.strip() for u in Path(args.urls).read_text().splitlines() if u.strip()]

    records, undated = [], 0
    for i, url in enumerate(urls, 1):
        stem = re.sub(r"[^a-zA-Z0-9]+", "_", url.split("/")[-1].split("?")[0])[:48]
        ext = ".jpg" if ".jp" in url.lower() else (".webp" if "webp" in url.lower() else ".png")
        dest = out / ("%02d_%s%s" % (i, stem, ext))
        if not http_download(url, dest):
            continue
        captured = args.captured or image_capture_date(dest) or "unknown"
        if captured == "unknown":
            undated += 1
        print("  -> %s  [%s]" % (dest.relative_to(REPO_ROOT), captured))
        records.append({"file": "%s/%s" % (args.category, dest.name), "source": args.source,
                        "url": url, "capture_date": captured,
                        "trust": TRUST.get(args.trust, 0)})

    mpath = pdir / "manifest.json"
    manifest = json.loads(mpath.read_text())
    bucket = BUCKETS.get(args.category, args.category)
    manifest.setdefault("evidence", {}).setdefault(bucket, []).extend(records)
    write_json(mpath, manifest)
    print("Downloaded %d/%d into %s" % (len(records), len(urls), out.relative_to(REPO_ROOT)))
    if undated:
        print("  !! %d image(s) have NO capture date. Layouts change between refurbs —"
              " undated photos can't be conflict-resolved. Pass --captured." % undated)


if __name__ == "__main__":
    main()

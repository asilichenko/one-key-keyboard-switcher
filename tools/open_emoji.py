import json
import time
import urllib.request
from pathlib import Path

# country-flag-emoji-json використовує OpenMoji SVG, має зручний JSON з кодами країн
INDEX_URL = "https://cdn.jsdelivr.net/npm/country-flag-emoji-json@2.0.0/dist/index.json"

PROJECT_ROOT: Path = Path(__file__).parent.parent
OUTPUT_PATH: Path = PROJECT_ROOT / "build/flags"


def load_svg_images(index_url: str = INDEX_URL, output_path: Path = OUTPUT_PATH) -> None:
    """Load SVG files by URL of JSON index and store as files"""

    # --- step 1: load index of all flags ---
    print("Loading index...")
    with urllib.request.urlopen(index_url) as r:
        flags = json.load(r)

    print(f"Found flags: {len(flags)}")

    # --- step 2: load each SVG ---

    output_path.mkdir(exist_ok=True)
    errors = []
    for i, flag in enumerate(flags):
        code = flag["code"]  # "UA", "US", "DE" ...
        url = flag["image"]  # CDN URL до SVG (OpenMoji)
        out = output_path / f"{code}.svg"

        if out.exists():
            continue

        try:
            with urllib.request.urlopen(url) as r:
                out.write_bytes(r.read())
            print(f"[{i + 1}/{len(flags)}] {code} OK")
        except Exception as e:
            print(f"[{i + 1}/{len(flags)}] {code} ERROR: {e}")
            errors.append(code)

        time.sleep(0.05)  # not to flood CDN

    if errors:
        print(f"\nFailed: {errors}")
    else:
        print("\nDone")


if __name__ == '__main__':
    load_svg_images()

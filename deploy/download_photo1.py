#!/usr/bin/env python3
"""Download photo1 attachments from Yandex Disk public links."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

LINKS = {
    "img817.jpg": "https://yadi.sk/d/KBawuYO_V_s55w",
    "sborka-6.jpg": "https://yadi.sk/d/scvO5iMlkB7Btg",
    "IMG_0872.JPG": "https://yadi.sk/d/40ZZ1GZsa3W0hg",
    "DSC_1506.JPG": "https://yadi.sk/d/muYwFSyMSbSgsg",
    "IMG_0330.JPG": "https://yadi.sk/d/3-LxyOWr2vbTSQ",
}

OUT = Path(__file__).resolve().parent.parent / "photo1"


def download(name: str, public_url: str) -> Path:
    api = (
        "https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key="
        + urllib.parse.quote(public_url, safe="")
    )
    with urllib.request.urlopen(api, timeout=120) as response:
        href = json.load(response)["href"]
    dest = OUT / name
    print(f"Downloading {name} ...")
    urllib.request.urlretrieve(href, dest)
    print(f"  -> {dest} ({dest.stat().st_size} bytes)")
    return dest


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, url in LINKS.items():
        download(name, url)


if __name__ == "__main__":
    main()

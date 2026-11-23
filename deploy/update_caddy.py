#!/usr/bin/env python3
"""Replace sandomirova block in /etc/caddy/Caddyfile."""

from __future__ import annotations

import re
import sys
from pathlib import Path

CADDY = Path("/etc/caddy/Caddyfile")
SNIPPET = Path("/tmp/sandomirova-caddy.snippet")


def main() -> None:
    if not SNIPPET.exists():
        raise SystemExit(f"Snippet not found: {SNIPPET}")

    snippet = SNIPPET.read_text(encoding="utf-8")
    if not CADDY.exists():
        CADDY.write_text(snippet, encoding="utf-8")
        print("Created Caddyfile with sandomirova block.")
        return

    text = CADDY.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\n# Static root: /var/www/sandomirova\.anspec\.ru\n\nsandomirova\.anspec\.ru \{.*?\n\}\n",
        re.S,
    )
    if pattern.search(text):
        text = pattern.sub("\n", text)
    elif "sandomirova.anspec.ru" in text:
        pattern2 = re.compile(r"\nsandomirova\.anspec\.ru \{.*?\n\}\n", re.S)
        text = pattern2.sub("\n", text)

    text = text.rstrip() + "\n\n" + snippet.strip() + "\n"
    CADDY.write_text(text, encoding="utf-8")
    print("Updated sandomirova Caddy block.")


if __name__ == "__main__":
    main()

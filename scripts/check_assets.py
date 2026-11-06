#!/usr/bin/env python
"""Offline integrity check for the supplied frontend resources (stdlib only)."""
import hashlib
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent

def main():
    manifest = json.loads((ROOT / "docs/original_asset_hashes.json").read_text(encoding="utf-8"))
    changed = {"js/site.js"}
    failures = []
    for name, expected in manifest.items():
        path = ROOT / "static" / name
        if not path.is_file():
            failures.append(f"Missing: {name}")
        elif name not in changed and hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            failures.append(f"Unexpected modification: {name}")
    references = set()
    for file in (ROOT / "templates").rglob("*.html"):
        text = file.read_text(encoding="utf-8")
        references.update(re.findall(r"{%\s*static\s+['\"]([^'\"]+)['\"]\s*%}", text))
    for name in references:
        if not (ROOT / "static" / name).is_file():
            failures.append(f"Missing template resource: {name}")
    if failures:
        print("\n".join(failures));return 1
    print(f"PASS: {len(manifest) - len(changed)} unchanged assets; {len(references)} distinct template references; transport JS present.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

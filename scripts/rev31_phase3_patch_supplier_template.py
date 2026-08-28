from __future__ import annotations
import argparse
from pathlib import Path
import re

CTA = """<div class="rev31-governance-entry" style="margin:12px 0;display:flex;gap:10px;flex-wrap:wrap;">
  <a href="/rev31-governance/sources" style="display:inline-block;padding:10px 14px;border:1px solid #18b6d9;border-radius:4px;text-decoration:none;">Add / Propose Supplier or Manufacturer</a>
  <a href="/rev31-governance/categories" style="display:inline-block;padding:10px 14px;border:1px solid #bbb;border-radius:4px;text-decoration:none;">Canonical Categories</a>
</div>
"""

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("path")
    args=ap.parse_args()
    p=Path(args.path)
    text=p.read_bytes().decode("utf-8")

    text=re.sub(
        r'(?is)\s*<div[^>]*class=["\']rev31-governance-entry["\'][^>]*>.*?</div>\s*',
        "\n",
        text,
    )

    patterns=[
        r'(?is)(<a\b[^>]*>.*?Open Supplier Browser.*?</a>)',
        r'(?is)(<button\b[^>]*>.*?Open Supplier Browser.*?</button>)',
    ]
    match=None
    for pattern in patterns:
        m=re.search(pattern,text)
        if m:
            match=m
            break
    if not match:
        raise RuntimeError("Could not locate complete Open Supplier Browser control safely.")

    text=text[:match.start()] + CTA + "\n" + text[match.start():]

    if text.count('/rev31-governance/sources') != 1:
        raise RuntimeError("Expected exactly one Governance source entry point after patch.")
    if "⊕" in text or "▦" in text:
        raise RuntimeError("Forbidden Revision 31 Unicode glyph found.")

    p.write_bytes(text.encode("utf-8"))
    print(f"PATCHED_UTF8={p}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())

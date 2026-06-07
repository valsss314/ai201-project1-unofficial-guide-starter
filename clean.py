"""
Write cleaned review files using the parser from ingest.py.

Reads the raw scrapes in professors/, strips all nav/header/footer boilerplate,
and writes one cleaned file per professor into professors_clean/. Each review is
formatted exactly like the chunks that get embedded (see ingest.to_chunk), with a
'---' divider between reviews. The raw professors/ files are left untouched.
"""

import os

from ingest import build_chunks, to_chunk

OUT_DIR = "professors_clean"
DIVIDER = "\n\n---\n\n"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    total = 0
    for source, name, reviews in build_chunks():
        body = DIVIDER.join(to_chunk(r) for r in reviews)
        out_path = os.path.join(OUT_DIR, source)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(body + "\n")
        print(f"  wrote {out_path:28s} {name:22s} {len(reviews):3d} reviews")
        total += len(reviews)
    print("-" * 60)
    print(f"  {total} cleaned reviews written to {OUT_DIR}/")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Place the finished front page for make.fun news-image-20261126.

The repository holds the completed 1024x1024 front page as entry.png.
Running this program writes an exact copy to
$MAKEFUN_OUTPUT_DIR/entry.png (falling back to /output/entry.png) and
refuses to report success unless the copy is itself a genuine 1024x1024
PNG. Only the Python standard library is used, and repeated runs write
identical bytes.

    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import sys
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PAGE_WIDTH = 1024
PAGE_HEIGHT = 1024


def describe_png(path):
    """Return (width, height) of the PNG at path, or raise ValueError."""
    blob = path.read_bytes()
    if blob[:8] != PNG_SIGNATURE:
        raise ValueError(f"{path} does not start with a PNG signature")
    if blob[12:16] != b"IHDR":
        raise ValueError(f"{path} has no IHDR chunk where one is expected")
    width, height = struct.unpack(">II", blob[16:24])
    return width, height


def main():
    source = Path(__file__).resolve().parent / "entry.png"
    if not source.is_file():
        print(f"error: {source} is missing", file=sys.stderr)
        return 1

    try:
        width, height = describe_png(source)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if (width, height) != (PAGE_WIDTH, PAGE_HEIGHT):
        print(f"error: entry.png is {width}x{height}, expected 1024x1024",
              file=sys.stderr)
        return 1

    destination_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / "entry.png"
    payload = source.read_bytes()
    destination.write_bytes(payload)
    if destination.read_bytes() != payload:
        print("error: copied bytes differ from entry.png", file=sys.stderr)
        return 1

    try:
        copied_width, copied_height = describe_png(destination)
    except ValueError as exc:
        print(f"error: copied file failed validation: {exc}", file=sys.stderr)
        return 1
    if (copied_width, copied_height) != (PAGE_WIDTH, PAGE_HEIGHT):
        print("error: copied entry.png is not 1024x1024", file=sys.stderr)
        return 1
    print(f"wrote {destination} "
          f"({destination.stat().st_size} bytes, {width}x{height})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

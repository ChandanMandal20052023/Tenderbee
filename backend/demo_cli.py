"""Compatibility entry point for the extraction-only document CLI."""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.extract_documents import main


if __name__ == "__main__":
    raise SystemExit(main())

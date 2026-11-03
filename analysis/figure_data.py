"""Plot data for the MATLAB figures in analysis/matlab/.

Python does the computation and writes each plotted series to a CSV in
analysis/figures/data/. The MATLAB scripts read those files (and committed
result files) and draw the PNG and PDF. Captions stay in Python, so every
number in a caption comes from the same values that are plotted.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "analysis/figures/data"
VARIANT_ORDER = ("V0", "V0P", "V1", "V2")
LETTERS = "abcdefghijkl"


def caption_path(figure: str | Path) -> Path:
    """``x/name.png`` -> ``x/name.caption.md``."""
    figure = Path(figure)
    return figure.with_name(figure.stem + ".caption.md")


def write_csv(path: str | Path, header, rows) -> Path:
    """Write one plot-data CSV with Unix line endings."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    return path

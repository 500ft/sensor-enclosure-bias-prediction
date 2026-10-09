"""Plot settings shared by the thermal figures.

Both README figures take variant colours, markers and text sizes from here, so
the same enclosure has the same colour in every plot.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

VARIANT_ORDER = ("V0", "V0P", "V1", "V2")
# Checked with a deuteranopia/protanopia simulation: every pair stays apart.
# The earlier green (V2) and purple (V0P) merged with red and blue.
VARIANT_COLORS = {"V0": "#c0392b", "V0P": "#882255", "V1": "#2980b9", "V2": "#e69f00"}
VARIANT_MARKERS = {"V0": "o", "V0P": "s", "V1": "^", "V2": "D"}
# Neutral marks. Under deuteranopia V0P turns mid grey, so keys and weather
# traces are black and the zero line is light grey.
KEY_COLOR = "#000000"
FORCING_COLOR = "#000000"   # weather inputs: no trace shares a variant hue
ZERO_COLOR = "#8a8a8a"
GRID_COLOR = "#e5e7eb"

# Three text sizes [pt]: titles and axis labels; legends and notes; tick labels.
BASE, SMALL, TICK = 9, 8, 7
LETTER = 11  # panel letters only
DPI = 300

RC = {
    "font.size": BASE,
    "axes.titlesize": BASE,
    "axes.labelsize": BASE,
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.axisbelow": True,
    "axes.linewidth": 0.8,
    "xtick.labelsize": TICK,
    "ytick.labelsize": TICK,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "legend.fontsize": SMALL,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "svg.hashsalt": "sensor-enclosure-figures",
    "svg.fonttype": "path",
}


@contextmanager
def style():
    """Apply the shared settings without changing global matplotlib state."""
    with plt.rc_context(RC):
        yield


def variant_label(vid: str, name: str) -> str:
    return f"{name} ({vid})"


def panel_letter(ax, letter: str) -> None:
    """Bold letter at the top left, outside the axes, level with the title."""
    ax.annotate(letter, xy=(0, 1), xycoords="axes fraction", xytext=(-26, 6),
                textcoords="offset points", fontsize=LETTER, fontweight="bold",
                ha="left", va="bottom")


def grid_y(ax) -> None:
    ax.grid(axis="y", color=GRID_COLOR, lw=0.6)


def save(fig, out_path) -> list[Path]:
    """Write the requested image at 300 dpi plus a same-name SVG.

    The SVG carries no date and fixed element ids, so a rerun with unchanged
    data gives the same file.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=DPI, metadata={"Date": None} if out.suffix.lower() in (".svg", ".pdf") else None)
    svg = out.with_suffix(".svg")
    if out.suffix.lower() != ".svg":
        fig.savefig(svg, metadata={"Date": None})
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    return [out, svg]

"""Plot settings shared by the thermal and synthetic-identifiability figures.

The canvas carries data, axes, tick labels, axis labels, panel letters and one
framed legend. Titles, notes and findings live in a caption file written next
to each image and repeated in the documents that show it.

- Each enclosure variant has one marker shape in every figure. Line style
  carries the other condition (solar load, schedule, duration). Colour is not
  used, so nothing depends on it.
- Nothing printed may touch another printed thing or the data. ``audit``
  returns every pair that does, and ``save`` refuses to write unless it is empty.
- Type is Computer Modern (matplotlib's bundled ``cmr10``) with mathtext "cm".
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.text import Text
from matplotlib.transforms import Bbox

VARIANT_ORDER = ("V0", "V0P", "V1", "V2")
VARIANT_MARKERS = {"V0": "o", "V0P": "s", "V1": "^", "V2": "D"}
INK = "black"
BAND = "#d4d4d4"   # 5th to 95th percentile band; a region, not a series colour
REFERENCE = {"color": INK, "lw": 0.6}
LETTERS = "abcdefghijkl"

# Three type sizes: axis labels and legend, panel letters, tick labels.
LABEL_SIZE, LETTER_SIZE, TICK_SIZE = 9, 9, 7
DPI = 600

RC = {
    "font.family": "serif",
    "font.serif": ["cmr10"],
    "mathtext.fontset": "cm",
    # cmr10 has no Unicode minus; mathtext tick labels carry a proper one.
    "axes.formatter.use_mathtext": True,
    "axes.unicode_minus": False,
    "font.size": LABEL_SIZE,
    "axes.labelsize": LABEL_SIZE,
    "legend.fontsize": LABEL_SIZE,
    "xtick.labelsize": TICK_SIZE,
    "ytick.labelsize": TICK_SIZE,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "axes.edgecolor": INK,
    "legend.frameon": True,
    "legend.fancybox": False,
    "legend.edgecolor": INK,
    "legend.framealpha": 1.0,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.dpi": DPI,
    "svg.hashsalt": "sensor-enclosure-figures",
    # Outlined SVG text renders the same where cmr10 is not installed.
    "svg.fonttype": "path",
}


@contextmanager
def style():
    """Apply the shared settings without changing global matplotlib state."""
    with plt.rc_context(RC):
        yield


def variant_label(vid: str, name: str) -> str:
    return f"{name} ({vid})"


def panel_letter(ax, index: int) -> None:
    """Letter "(a)", "(b)", ... above the top left corner of the axes."""
    ax.text(0, 1.04, f"({LETTERS[index]})", transform=ax.transAxes,
            ha="left", va="bottom", size=LETTER_SIZE)


def audit(fig) -> list[tuple[str, str]]:
    """Pairs of printed things whose boxes touch. Empty means the canvas is clean.

    Every drawn text (tick labels inside the view, axis labels, panel letters,
    legend entries) is checked against every other drawn text, against the
    data drawn in each axes (clipped to the axes, as it is rendered) and against
    each legend frame. Data is not checked against data. Texts inside a legend
    are not checked against their own frame.
    """
    with style():  # ticks created while drawing take the shared fonts
        fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    legends = list(fig.legends) + [ax.get_legend() for ax in fig.axes if ax.get_legend()]
    owner = {id(child): legend for legend in legends for child in legend.findobj()}
    tick_labels, drawn = set(), []
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            low, high = sorted(axis.get_view_interval())
            slack = 1e-9 * (high - low)
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                for label in (tick.label1, tick.label2):
                    tick_labels.add(id(label))
                    if label.get_visible() and label.get_text().strip() and low - slack <= tick.get_loc() <= high + slack:
                        drawn.append(label)
    drawn += [t for t in fig.findobj(Text)
              if id(t) not in tick_labels and t.get_visible() and t.get_text().strip()]
    texts = [(f"text {t.get_text()!r}", t.get_window_extent(renderer).padded(1), owner.get(id(t))) for t in drawn]
    others = []
    for ax in fig.axes:
        for line in ax.lines:
            box = Bbox.intersection(line.get_window_extent(renderer), ax.bbox) if line.get_clip_on() \
                else line.get_window_extent(renderer)
            if box is not None:
                others.append((f"data in {ax.get_ylabel() or 'axes'}", box, None))
    others += [("legend frame", legend.get_window_extent(renderer), legend) for legend in legends]
    hits = []
    for i, (name_a, box_a, legend_a) in enumerate(texts):
        for name_b, box_b, legend_b in texts[i + 1:] + others:
            if legend_a is not None and legend_a is legend_b:
                continue
            if box_a.overlaps(box_b):
                hits.append((name_a, name_b))
    return hits


def save(fig, out_path) -> list[Path]:
    """Write the requested image at 600 dpi plus a same-name SVG; refuse a touching canvas.

    The SVG carries no date and fixed element ids, so a rerun with unchanged
    data gives the same file.
    """
    hits = audit(fig)
    if hits:
        raise ValueError(f"printed items touch: {hits}")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    svg = out.with_suffix(".svg")
    with style():  # the SVG and dpi settings are read at save time
        fig.savefig(out, dpi=DPI, metadata={"Date": None} if out.suffix.lower() in (".svg", ".pdf") else None)
        if out.suffix.lower() != ".svg":
            fig.savefig(svg, metadata={"Date": None})
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    return [out, svg]


def caption_path(out_path) -> Path:
    """``<stem>.caption.md`` beside the image."""
    return Path(out_path).with_suffix(".caption.md")

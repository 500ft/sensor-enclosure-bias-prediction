"""Shared checks for the figure tests: printed text and caption placement."""
from pathlib import Path

from matplotlib.text import Text

ROOT = Path(__file__).resolve().parents[2]


def printed(fig):
    return {t.get_text() for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()}


def axis_text(fig):
    """Tick labels, axis labels and legend entries: the text a data-only canvas may hold."""
    allowed = {t.get_text() for legend in fig.legends for t in legend.get_texts()}
    for ax in fig.axes:
        allowed |= {t.get_text() for t in ax.get_xticklabels(which="both") + ax.get_yticklabels(which="both")}
        allowed |= {ax.get_xlabel(), ax.get_ylabel()}
    allowed.add(fig.get_supxlabel())
    return allowed


def squash(text):
    return " ".join(text.split())

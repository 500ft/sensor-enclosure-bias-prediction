"""Shared helpers for the figure tests: repository paths and the MATLAB outputs."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIGURES = ROOT / "analysis/figures"
MATLAB = ROOT / "analysis/matlab"


def squash(text):
    return " ".join(text.split())


def check_matlab_outputs(case, stem, script, data_names):
    """The committed PNG and PDF exist, and the drawing script reads the named data files."""
    png, pdf = FIGURES / f"{stem}.png", FIGURES / f"{stem}.pdf"
    case.assertEqual(png.read_bytes()[:8], b"\x89PNG\r\n\x1a\n", png)
    case.assertEqual(pdf.read_bytes()[:5], b"%PDF-", pdf)
    case.assertFalse((FIGURES / f"{stem}.svg").exists(), "the PDF replaces the SVG companion")
    source = (MATLAB / script).read_text()
    for name in data_names:
        case.assertIn(name, source, script)
    case.assertIn(script[:-2], (MATLAB / "render_figures.m").read_text())

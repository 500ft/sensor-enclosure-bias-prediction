# MATLAB figures and tables

These scripts draw the repository's data figures and typeset its steady result
tables. Python does all computation; MATLAB only reads plot data and committed
results. Tested with MATLAB R2025b.

## Regenerate

From the repository root:

```bash
# 1. Plot data and captions (Python). Temporary table paths keep the committed CSVs untouched.
python analysis/thermal_bias.py --table /tmp/enclosure-day.csv --night-table /tmp/enclosure-night.csv
python -m analysis.thermal_transient --json /tmp/enclosure-transient.json
python -m analysis.render_identifiability

# 2. Figures and table fragments (MATLAB)
matlab -batch "addpath('analysis/matlab'); render_figures"
```

Step 1 writes `analysis/figures/data/*.csv` and the `*.caption.md` files. Step 2
writes `analysis/figures/<name>.png` (300 dpi) and `<name>.pdf` (vector) for the
four figures, and the LaTeX fragments in `analysis/figures/tables/`. Each output
runs in its own `try`/`catch`; the call exits with an error if any output failed.

To typeset one table fragment as PDF and PNG, with LuaLaTeX (or Tectonic) and Poppler:

```bash
cd "$(mktemp -d)"
cp "$OLDPWD/analysis/matlab/table_page.tex" .
cp "$OLDPWD/analysis/figures/tables/predicted_rise_table.tex" fragment.tex
lualatex table_page.tex
pdftoppm -r 300 -png -singlefile table_page.pdf predicted_rise_table
```

## Files

| Script | Reads | Writes |
| --- | --- | --- |
| `render_figures.m` | all of the below | runs every script |
| `make_thermal_bias.m` | `figures/data/thermal_bias_sweep.csv`, `output/thermal_bias_table.csv` | `thermal_bias.png`, `.pdf` |
| `make_thermal_transient.m` | `figures/data/thermal_transient_series.csv` | `thermal_transient_prediction.png`, `.pdf` |
| `make_identifiability_profiles.m` | `figures/data/synthetic_identifiability_profiles.csv`, `input/identifiability_design.json` | `synthetic_identifiability_profiles.png`, `.pdf` |
| `make_identifiability_tradeoffs.m` | `output/synthetic_identifiability.csv`, `input/identifiability_design.json` | `synthetic_identifiability_tradeoffs.png`, `.pdf` |
| `make_rise_table.m` | `output/thermal_bias_table.csv` | `tables/predicted_rise_table.tex` |
| `make_result_tables.m` | `output/thermal_bias_table.csv`, `output/thermal_bias_night_table.csv` | `tables/thermal_bias_temperature_table.tex`, `thermal_bias_rh_table.tex`, `painted_control_table.tex`, `night_table.tex` |
| `make_interval_table.m` | `output/thermal_bias_uncertainty.csv`, `output/thermal_bias_uncertainty.json` | `tables/thermal_bias_interval_table.tex` |
| `fig_style.m`, `export_pair.m`, `panel_title.m` | — | shared style, PDF + PNG export, panel letters |

Paths in the table are relative to `analysis/`.

## Style

`fig_style.m` sets LaTeX text everywhere (Computer Modern), 9 pt axis labels,
8 pt notes, 7 pt ticks and 10 pt bold panel letters. MATLAB's default blue is the
first series and its default orange the second; line style or marker fill gives
each a second cue. Reference lines are grey and dotted. Figures carry no titles;
findings go in the caption files. MATLAB's LaTeX interpreter rejects `\small` and
`\footnotesize`, so `panel_title.m` sets the 8 pt panel names with `\fontsize`.

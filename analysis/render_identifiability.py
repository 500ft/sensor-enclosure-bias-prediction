"""Export compact results and render the synthetic design aid from its checkpoint."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from analysis import figure_style as fs
from analysis import synthetic_identifiability as study
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import NullFormatter


def width(record, field):
    sets=record[field]
    if any(s['open_low'] or s['open_high'] for s in sets): return None
    return sum(np.log(s['high']/s['low']) for s in sets if s['low']>0)


def export(checkpoint, refinement, output):
    run=json.loads(checkpoint.read_text()); verification=json.loads(refinement.read_text())
    assert verification['checkpoint_sha256']==study.sha(checkpoint)
    cfg=run['config']; cells=run['cells']; index={c['key']:c for c in cells}
    comparisons=[]
    for c in cells:
        baseline=index[f"{c['scenario']}__tau{c['tau_s']}__duration{min(cfg['duration_s'])}__{c['schedule']}"]
        values=[]
        for a,b in zip(c['records'],baseline['records']):
            wa,wb=width(a,'gain_sets_k_per_w'),width(b,'gain_sets_k_per_w')
            if wa and wb: values.append(np.log(wb/wa))
        comparisons.append({'key':c['key'],'closed_pairs':len(values),
                            'median_log_width_ratio_vs_shortest':float(np.median(values)) if values else None})
    paired=[]
    for c in cells:
        if c['schedule']!='repeated_steps': continue
        other=index[c['key'].replace('repeated_steps','single_step')]
        diffs=[]
        for a,b in zip(c['records'],other['records']):
            wa,wb=width(a,'gain_sets_k_per_w'),width(b,'gain_sets_k_per_w')
            if wa and wb: diffs.append(np.log(wb/wa))
        paired.append({'scenario':c['scenario'],'tau_s':c['tau_s'],'duration_s':c['duration_s'],
                       'closed_pairs':len(diffs),'median_log_single_over_repeated_width':float(np.median(diffs)) if diffs else None})
    # Retain all profiles in compressed numeric form, with cell order in JSON.
    arrays={}
    for i,c in enumerate(cells):
        for key in ('tau_s','delta_sse','gain_profile_k_per_w'):
            arrays[f'cell{i}_{key}']=np.array(c['profile'][key])
        c['multiple_starts']=c['profile']['starts'];del c['profile']
    profile_path=output.with_name(f'{output.stem}_profiles.npz')
    np.savez_compressed(profile_path,**arrays)
    result={k:v for k,v in run.items() if k not in ('pid','config')}
    result['config_file']=run.get('config_file','analysis/input/identifiability_design.json')
    result['checkpoint_sha256']=study.sha(checkpoint)
    result['profile_file']=profile_path.name; result['profile_sha256']=study.sha(profile_path)
    result['refinement']=verification;result['duration_information']=comparisons;result['paired_schedule_widths']=paired
    result['complete']=len(cells)==len(cfg['tau_s'])*len(cfg['duration_s'])*len(cfg['schedules'])*len(cfg['scenarios'])
    if 'amends_result' in cfg:
        result['cadence_comparison']=cadence_comparison(run['summary'],cfg)
    output.write_text(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n')
    with output.with_suffix('.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=run['summary'][0].keys(),lineterminator='\n');writer.writeheader();writer.writerows(run['summary'])
    return result


COMPARED = ('gain_open_fraction', 'gain_coverage', 'tau_open_fraction', 'tau_coverage')


def cadence_comparison(summary, cfg):
    """Amended-run cell values beside the registered run's, matched by scenario, tau, schedule and duration rank."""
    parent_cfg_path = study.ROOT / cfg['amends']
    assert study.sha(parent_cfg_path) == cfg['amends_sha256'], 'registered design changed since the amendment'
    pcfg = json.loads(parent_cfg_path.read_text())
    parent = json.loads((study.ROOT / cfg['amends_result']).read_text())
    rank = lambda c, d: sorted(c['duration_s']).index(d)
    index = {(r['scenario'], r['tau_s'], r['schedule'], rank(pcfg, r['duration_s'])): r for r in parent['summary']}
    rows = []
    for r in summary:
        p = index[(r['scenario'], r['tau_s'], r['schedule'], rank(cfg, r['duration_s']))]
        row = {'key': r['key'], 'parent_key': p['key'], 'scenario': r['scenario'], 'tau_s': r['tau_s'],
               'schedule': r['schedule'], 'duration_s': r['duration_s'], 'parent_duration_s': p['duration_s'],
               'input_energy_j': r['input_energy_j'], 'parent_input_energy_j': p['input_energy_j']}
        for f in COMPARED:
            row[f], row['parent_' + f], row[f + '_change'] = r[f], p[f], r[f] - p[f]
        rows.append(row)
    return {'parent_result': cfg['amends_result'], 'parent_config': cfg['amends'], 'parent_dt_s': pcfg['dt_s'],
            'dt_s': cfg['dt_s'], 'matching': 'scenario, tau, schedule and duration rank; parameter draws shared, '
            'noise realizations not', 'rows': rows}


def config_of(result):
    return json.loads((study.ROOT / result['config_file']).read_text())


def cfg_relative(result):
    """Config path relative to analysis/, for links from the generated report."""
    return str(Path(result['config_file']).relative_to('analysis'))


def stem_of(result):
    """'synthetic_identifiability' from 'synthetic_identifiability_profiles.npz'."""
    return result['profile_file'][:-len('_profiles.npz')]


def hours(seconds):
    return f'{seconds / 3600:.3g}'


# Scenario order and the words the profile caption uses for each panel.
SCENARIOS = (('matched', 'matched dynamics with quantization'),
             ('noisy', 'higher noise with coarser quantization'),
             ('ambient_mismatch', 'an unobserved ambient excursion'),
             ('probe_lag', 'additional probe lag'))
MARKERS = ('o', 's', '^'); STYLES = ('-', '--', ':')
MARKER_NAMES = {'o': 'circles', 's': 'squares', '^': 'triangles'}
STYLE_NAMES = {'-': 'solid', '--': 'dashed', ':': 'dotted'}
PROFILE_YMAX = 12
GENERATING = {'color': fs.INK, 'lw': 0.7, 'ls': '-.'}


def duration_sources(result):
    stem = stem_of(result)
    return (f'`analysis/output/{stem}.json`, `analysis/output/{stem}_profiles.npz` and '
            f'`{result["config_file"]}`')


def profile_cells(result, cfg):
    """Cell index per (scenario, duration): slowest heater, repeated steps."""
    return {(s, d): next(i for i, c in enumerate(result['cells'])
                         if c['scenario'] == s and c['tau_s'] == max(cfg['tau_s'])
                         and c['duration_s'] == d and c['schedule'] == 'repeated_steps')
            for s, _ in SCENARIOS for d in cfg['duration_s']}


def tradeoff_rows(result, cfg):
    """(row, tau, schedule) -> summary rows sorted by duration; row 0 matched, row 1 mismatch."""
    out = {}
    for row, scenario in enumerate(('matched', 'ambient_mismatch')):
        for tau in cfg['tau_s']:
            for sch in cfg['schedules']:
                out[row, tau, sch] = sorted([r for r in result['summary'] if r['scenario'] == scenario
                                             and r['tau_s'] == tau and r['schedule'] == sch],
                                            key=lambda r: r['duration_s'])
    return out


def styles_phrase(labels):
    """'circles with solid lines, A; squares with dashed lines, B.' in plotting order."""
    return '; '.join(f'{MARKER_NAMES[m]} with {STYLE_NAMES[ls]} lines, {label}'
                     for m, ls, label in zip(MARKERS, STYLES, labels)) + '.'


def profiles_caption(result, cfg):
    hrs = [hours(d) for d in cfg['duration_s']]
    panels = '; '.join(f"({fs.LETTERS[i]}) {words}" for i, (_, words) in enumerate(SCENARIOS))
    return (
        "Synthetic development example, not physical data. Profile likelihood-ratio statistic against "
        "candidate C/G for the first registered draw of each scenario, with the slowest generating heater "
        f"time constant ({max(cfg['tau_s']) / 60:g} min) and repeated power steps: {panels}. "
        f"Record length: {styles_phrase([h + ' h' for h in hrs])} Panels share axes. The thin horizontal line "
        f"is the nominal likelihood-ratio cutoff, {cfg['profile_delta_chi2']:.2f}. The dash-dot vertical "
        "line marks the generating heater time constant; in the probe-lag case there is no true "
        f"single-node time constant. Curves are clipped above {PROFILE_YMAX}; the full-range profiles are "
        f"retained. Sources: {duration_sources(result)}."
    )


def tradeoffs_caption(result, cfg):
    rows = tradeoff_rows(result, cfg)
    schedules = list(cfg['schedules'])
    longest = max(cfg['duration_s'])
    open_long = max(r['gain_open_fraction'] for (row, _, _), rs in rows.items() if row == 0
                    for r in rs if r['duration_s'] == longest)
    cover_long = max(r['gain_coverage'] for (row, _, _), rs in rows.items() if row == 1
                     for r in rs if r['duration_s'] == longest)
    n_tau = len(cfg['tau_s'])
    fields = ('gain_open_fraction', 'gain_coverage')
    series = {(row, tau): [tuple(r[fields[row]] for r in rows[row, tau, s]) for s in schedules]
              for row in range(2) for tau in cfg['tau_s']}
    letter = {key: f"({fs.LETTERS[row * n_tau + col]})"
              for col, tau in enumerate(cfg['tau_s']) for row in range(2) for key in [(row, tau)]}
    same = [letter[key] for key, (a, b) in series.items() if a == b]
    touching = any(x == y for a, b in series.values() for x, y in zip(a, b))
    coincide = ((" Where both schedules give the same value, the square covers the circle"
                 + (f"; in {' and '.join(same)} that holds at every duration" if same else "") + ".")
                if touching else "")
    first = 'no' if open_long == 0 else f'at most {100 * open_long:g} % of'
    return (
        "Synthetic development example, not physical data. Each point is the fraction of "
        f"{cfg['replicates_per_cell']} draws in one cell at equal input energy. Columns are generating C/G of "
        f"{', '.join(f'{t / 60:g}' for t in cfg['tau_s'][:-1])} and {cfg['tau_s'][-1] / 60:g} min. "
        f"Panels (a) to ({fs.LETTERS[n_tau - 1]}), matched dynamics: the fraction of gain (eta/G) profile "
        f"sets that reach the registered search edge. Panels ({fs.LETTERS[n_tau]}) to "
        f"({fs.LETTERS[2 * n_tau - 1]}), unobserved ambient excursion: the fraction of gain sets that "
        f"contain the true eta/G; the thin horizontal line is the nominal {100 * cfg['profile_level']:g} % "
        "level, not a measured performance target. "
        f"Schedule: {styles_phrase([s.replace('_', ' ') for s in schedules])} Lines connect the discrete durations "
        f"{', '.join(hours(d) for d in cfg['duration_s'][:-1])} and {hours(longest)} h and do not "
        f"establish interpolation to an untested schedule.{coincide} Longer observations can narrow sets "
        f"while unmodeled drift defeats coverage: at {hours(longest)} h {first} matched gain sets reach "
        f"the search edge, and ambient-excursion coverage is at most {100 * cover_long:g} %. Sources: "
        f"`analysis/output/{stem_of(result)}.csv` and `{result['config_file']}`."
    )


def profiles_figure(result, profiles, cfg):
    cells = profile_cells(result, cfg)
    with fs.style():
        fig, axs = plt.subplots(2, 2, figsize=(7.2, 5.4), sharex=True, sharey=True)
        for k, (ax, (scenario, _)) in enumerate(zip(axs.flat, SCENARIOS)):
            for j, duration in enumerate(cfg['duration_s']):
                idx = cells[scenario, duration]
                ax.plot(profiles[f'cell{idx}_tau_s'] / 60, profiles[f'cell{idx}_delta_sse'], color=fs.INK,
                        lw=1.0, ls=STYLES[j], marker=MARKERS[j], markevery=130, ms=3.5)
            ax.axhline(cfg['profile_delta_chi2'], zorder=1, **fs.REFERENCE)
            ax.axvline(max(cfg['tau_s']) / 60, zorder=1, **GENERATING)
            ax.set(xscale='log', ylim=(0, PROFILE_YMAX))
            ax.tick_params(length=3, which='both')
            fs.panel_letter(ax, k)
        for ax in axs[1]:
            ax.set_xlabel('Candidate $C/G$ [min]')
        for ax in axs[:, 0]:
            ax.set_ylabel('Profile likelihood-ratio\nstatistic')
        keys = [Line2D([], [], color=fs.INK, lw=1.0, ls=STYLES[j], marker=MARKERS[j], ms=3.5,
                       label=f'{hours(d)} h') for j, d in enumerate(cfg['duration_s'])]
        keys += [Line2D([], [], label='Nominal cutoff', **fs.REFERENCE),
                 Line2D([], [], label='Generating $C/G$', **GENERATING)]
        fig.legend(handles=keys, loc='upper center', bbox_to_anchor=(0.5, 0.995), ncol=len(keys),
                   handlelength=2.4, columnspacing=1.2, borderaxespad=0)
        fig.subplots_adjust(left=0.095, right=0.985, bottom=0.09, top=0.89, wspace=0.12, hspace=0.25)
    return fig


def tradeoffs_figure(result, cfg):
    rows = tradeoff_rows(result, cfg)
    n_tau = len(cfg['tau_s'])
    with fs.style():
        fig, axs = plt.subplots(2, n_tau, figsize=(7.2, 4.8), sharex=True, sharey=True)
        for col, tau in enumerate(cfg['tau_s']):
            for j, sch in enumerate(cfg['schedules']):
                for row, field in enumerate(('gain_open_fraction', 'gain_coverage')):
                    rs = rows[row, tau, sch]
                    axs[row, col].plot([r['duration_s'] / 3600 for r in rs], [r[field] for r in rs], color=fs.INK,
                                       lw=1.0, ls=STYLES[j], marker=MARKERS[j], ms=4)
            axs[1, col].axhline(cfg['profile_level'], zorder=1, **fs.REFERENCE)
        hrs = [d / 3600 for d in cfg['duration_s']]
        for k, ax in enumerate(axs.flat):
            ax.set(xscale='log', ylim=(-.04, 1.04))
            ax.set_xticks(hrs, [hours(d) for d in cfg['duration_s']])
            ax.xaxis.set_minor_formatter(NullFormatter())
            ax.tick_params(length=3, which='both')
            fs.panel_letter(ax, k)
        for ax in axs[1]:
            ax.set_xlabel('Observation duration [h]')
        axs[0, 0].set_ylabel('Gain sets at search\nedge [fraction]')
        axs[1, 0].set_ylabel('Gain sets containing\ntrue $\\eta/G$ [fraction]')
        keys = [Line2D([], [], color=fs.INK, lw=1.0, ls=STYLES[j], marker=MARKERS[j], ms=4,
                       label=sch.replace('_', ' ').capitalize()) for j, sch in enumerate(cfg['schedules'])]
        keys.append(Line2D([], [], label='Nominal coverage level', **fs.REFERENCE))
        fig.legend(handles=keys, loc='upper center', bbox_to_anchor=(0.5, 0.995), ncol=len(keys),
                   handlelength=2.4, columnspacing=1.2, borderaxespad=0)
        fig.subplots_adjust(left=0.105, right=0.985, bottom=0.10, top=0.88, wspace=0.12, hspace=0.25)
    return fig


def plot(result, output, figures):
    cfg = config_of(result)
    stem = stem_of(result)
    profiles = np.load(output.with_name(result['profile_file']))
    for name, fig, text in (
            (f'{stem}_profiles.png', profiles_figure(result, profiles, cfg),
             profiles_caption(result, cfg)),
            (f'{stem}_tradeoffs.png', tradeoffs_figure(result, cfg),
             tradeoffs_caption(result, cfg))):
        fs.save(fig, figures / name)
        plt.close(fig)
        fs.caption_path(figures / name).write_text(text + '\n')


def comparison_section(result, cfg):
    """Generated from the cadence_comparison block: the longest-duration slice, every scenario."""
    cc = result['cadence_comparison']; dt, pdt = cc['dt_s'], cc['parent_dt_s']
    n = cfg['replicates_per_cell']; two_se = 2 * 100 * np.sqrt(.25 / n)
    longest = max(cfg['duration_s']); shortest = min(r['duration_s'] for r in cc['rows'])
    short = next(r for r in cc['rows'] if r['duration_s'] == shortest)
    rows = [r for r in cc['rows'] if r['duration_s'] == longest]
    matched = [r for r in rows if r['scenario'] == 'matched']
    parent_stem = Path(cc['parent_result']).stem
    pct = lambda v: f"{100 * v:.1f}"
    drop = min(rows, key=lambda r: r['gain_coverage_change'])
    lines = [f"## Comparison with the registered {pdt:g} s run", "",
             f"Cadence {dt:g} s against the registered {pdt:g} s ([result]({parent_stem}.json), "
             f"[CSV]({parent_stem}.csv)). Cells are matched by scenario, time constant, schedule and duration rank. "
             f"The shortest cell is {hours(shortest)} h here against {hours(short['parent_duration_s'])} h registered, "
             f"with {100 * (short['input_energy_j'] / short['parent_input_energy_j'] - 1):.1f} % more input energy; "
             "the other durations and energies are equal. Coupling, offset and excursion-phase draws are shared "
             "between the two runs; noise realizations are not. "
             f"Each cell has {n} draws, so a change below {two_se:.0f} percentage points is within two Monte Carlo standard errors. "
             "Per-cell values and changes: `cadence_comparison` in the numeric result.", "",
             f"| Scenario | C/G [min] | Schedule | Gain open [%] {pdt:g} s | Gain open [%] {dt:g} s | Gain coverage [%] {pdt:g} s | Gain coverage [%] {dt:g} s | Time-constant open [%] {pdt:g} s | Time-constant open [%] {dt:g} s |",
             "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in rows:
        lines.append(f"| {r['scenario'].replace('_', ' ')} | {r['tau_s'] / 60:g} | {r['schedule'].replace('_', ' ')} | "
                     f"{pct(r['parent_gain_open_fraction'])} | {pct(r['gain_open_fraction'])} | {pct(r['parent_gain_coverage'])} | "
                     f"{pct(r['gain_coverage'])} | {pct(r['parent_tau_open_fraction'])} | {pct(r['tau_open_fraction'])} |")
    lines += ["",
              f"All rows are the {hours(longest)} h duration. Under matched dynamics at {hours(longest)} h, gain sets reach the "
              f"search edge in {sum(r['gain_open_fraction'] > 0 for r in matched)} of {len(matched)} cells at {dt:g} s "
              f"({sum(r['parent_gain_open_fraction'] > 0 for r in matched)} at {pdt:g} s); the largest open fraction is "
              f"{pct(max(r['gain_open_fraction'] for r in matched))} % ({pct(max(r['parent_gain_open_fraction'] for r in matched))} % at {pdt:g} s). "
              f"Matched gain coverage is at least {pct(min(r['gain_coverage'] for r in matched))} % "
              f"({pct(min(r['parent_gain_coverage'] for r in matched))} % at {pdt:g} s). Over all {len(rows)} cells at this duration, "
              f"the largest coverage change is {100 * drop['gain_coverage_change']:+.1f} percentage points in `{drop['key']}`; "
              f"{sum(r['gain_coverage_change'] < -two_se / 100 for r in rows)} cells fall and "
              f"{sum(r['gain_coverage_change'] > two_se / 100 for r in rows)} rise by more than {two_se:.0f} points.", ""]
    return lines


def report(result, path):
    cfg=config_of(result); stem=stem_of(result); ref=result['refinement']
    n=cfg['replicates_per_cell']; count=sum(len(c['records']) for c in result['cells'])
    failures=[c for c in ref['cells'] if c['max_start_excess_sse']>1e-6]
    amended='cadence_comparison' in result
    lines=["# Executed synthetic I1 design aid"+(f" at {cfg['dt_s']:g} s sampling cadence (registered amendment)" if amended else ""), "",
           f"Executed {len(result['cells'])} scenario cells with {count} synthetic fits. Estimation-only reporting is retained.", "",
           f"Source: [numeric result]({stem}.json), [all-cell CSV]({stem}.csv), "
           f"[profile arrays]({stem}_profiles.npz). This page is generated from those outputs.", ""]
    if amended:
        lines += [f"Registration: [amendment file](../{cfg_relative(result)}), which amends the registered design "
                  "and records why the shortest cell changed. The design aid, its limits and the pending physical inputs are "
                  "unchanged; this run tests the sampling cadence only.", ""] + comparison_section(result, cfg)
    else:
        lines += ["## What the calculation supports", "",
           "Power-only interventions identify C/G and eta/G under the single-node model. "
           "Jointly scaling C, G and eta leaves the trajectory invariant. "
           "The [derivation and registration](../identifiability_design.md) explain which independent heat-path input would fix the scale.", "",
           "Longer records usually reduce open profiles in the matched scenarios. "
           "The isolated power block gives narrower gain sets than the repeated schedule in the matched cells where both sets close. "
           "This compares equal energy and duration under these assumed response/noise conditions; it does not remove the physical protocol's replication and counterbalancing requirement.", "",
           "Ambient mismatch can produce narrow sets with poor coverage. Extra probe lag also biases the single-node interpretation. "
           "A small residual variance alone does not establish an adequate thermal structure. "
           "No physical detection limit, preferred enclosure or calibration-transfer performance follows from this study.", ""]
    durations=f"{', '.join(hours(d) for d in cfg['duration_s'][:-1])} and {hours(max(cfg['duration_s']))} h"
    lines += ["## Slow-response comparison", "",
           f"Generating heater time constant: {max(cfg['tau_s'])/60:g} min. "
           "Every registered duration and schedule is shown for this slice; other time constants remain in the CSV. "
           "Open means a profile set reaches the registered search boundary. Coverage uses all draws, including open sets.", "",
           "| Scenario | Duration [h] | Schedule | Gain coverage [%] | Gain open [%] | Time-constant open [%] |",
           "| --- | ---: | --- | ---: | ---: | ---: |"]
    for r in result['summary']:
        if r['tau_s']==max(cfg['tau_s']):
            lines.append(f"| {r['scenario'].replace('_',' ')} | {hours(r['duration_s'])} | {r['schedule'].replace('_',' ')} | {100*r['gain_coverage']:.1f} | {100*r['gain_open_fraction']:.1f} | {100*r['tau_open_fraction']:.1f} |")
    lines += ["", "## Profiles and schedule tradeoffs", "",
              f"![Profile likelihood-ratio curves for {durations} records in four synthetic scenarios, with the nominal cutoff and generating time constant](../figures/{stem}_profiles.png)", "",
              profiles_caption(result, cfg), "",
              f"[Caption](../figures/{stem}_profiles.caption.md) · "
              f"[Vector profiles](../figures/{stem}_profiles.svg).", "",
              f"![Gain-set openness under matched dynamics and gain coverage under an ambient excursion, by observation duration and schedule](../figures/{stem}_tradeoffs.png)", "",
              tradeoffs_caption(result, cfg), "",
              f"[Caption](../figures/{stem}_tradeoffs.caption.md) · "
              f"[Vector tradeoffs](../figures/{stem}_tradeoffs.svg).", "",
              "The JSON duration_information entries give paired log width reduction relative to the shortest same-schedule record. "
              "paired_schedule_widths compares single versus repeated steps. Positive values mean narrower repeated-step sets. "
              "These are descriptive information proxies, not Bayesian information or entropy. Only pairs with both sets closed contribute; their counts are reported. "
              "Null means no eligible pair. They must be read alongside openness and coverage, rather than used to rank schedules alone.", "",
              "## Numerical validation and resource use", "",
              f"The refinement doubled profile-grid resolution to {ref['refined_grid_count']} points on the same draws. "
              f"Time-constant coverage changed in {ref['tau_coverage_changes']} fits and gain coverage in {ref['gain_coverage_changes']} fits. "
              f"Maximum relative estimate changes were {100*ref['max_tau_hat_relative_change']:.2f}% for time constant and {100*ref['max_gain_hat_relative_change']:.2f}% for gain. "
              "The discrete grid includes each generating time constant to avoid an off-grid truth; this favors recovery slightly compared with an unknown physical parameter. Grid agreement on coverage does not prove continuous optimization accuracy or calibrated uncertainty.", "",
              f"Discrete profile descent from the registered starts reached inferior minima in {len(failures)} first-draw cells. "
              f"The largest excess likelihood-ratio statistic was {ref['max_start_excess_sse']:.2f}. "
              "Published fits instead use the minimum across the entire registered grid. "
              "The per-cell multiple_starts records preserve these failures; each key and seed regenerates its input.", "",
              f"Exact response superposition, independent RK4, joint-scaling trajectories and interval energy checks passed. "
              f"Maximum interval-energy residual: {result['validation']['interval_energy_max_j']:.2e} J. "
              "A direct GLS solve independently checked variable projection, and the AR(1) whitening norm matched the full covariance inverse.", "",
              "| Computation | Elapsed [s] | Peak RSS [MiB] |", "| --- | ---: | ---: |",
              f"| Registered matrix | {result['elapsed_s']:.2f} | {result['peak_rss_bytes']/2**20:.1f} |",
              f"| Profile refinement | {ref['elapsed_s']:.2f} | {ref['peak_rss_bytes']/2**20:.1f} |", "",
              f"Raw synthetic arrays: {result['raw_bytes']/2**20:.2f} MiB, retained outside git with per-file hashes. "
              "Both runs used one worker and one BLAS/OpenMP thread. Checkpoints contain the exact configuration, generator hash and completed cells.", "",
              "## Interpretation limits and next input", "",
              f"Each cell has {n} Monte Carlo draws. The maximum binomial Monte Carlo standard error is {100*np.sqrt(.25/n):.1f} percentage points; "
              "the small batches describe failure regimes and do not precisely calibrate nominal coverage. "
              "Schedules and durations share random draws; cells are not independent physical replications. "
              "Known noise covariance is optimistic, quantization is omitted from the fit covariance, and the ambient excursion period scales with observation duration. "
              "Thus the mismatch duration comparison changes both exposure length and drift time scale. Constant calibration offset is profiled as a nuisance; time-varying calibration and power-meter errors need actual specifications.", "",
              "The profile sets are asymptotic marginal likelihood-ratio sets over finite search domains. "
              "Disconnected components and open edges are retained. The CSV's finite-domain widths include truncation and must not be read as finite uncertainty bounds. "
              "For probe-lag rows, time-constant inclusion only asks whether the generating heater constant is inside the fitted set; it is not valid coverage of a nonexistent single-node truth.", "",
              "The owner still supplies the [meeting and rig inputs](../../docs/COLOCATION_OWNER_SESSION.md#current-blocker). "
              "Actual response, ambient-channel quality, noise, calibrated power/coupling and airflow independence could change the schedule comparison. "
              "Physical M1/M2, I1, protocol freeze and held-out-design comparison remain pending.", ""]
    path.write_text('\n'.join(lines))


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint',type=Path);ap.add_argument('--refinement',type=Path)
    ap.add_argument('--output',type=Path,default=study.ROOT/'analysis/output/synthetic_identifiability.json')
    ap.add_argument('--figures',type=Path,default=study.ROOT/'analysis/figures');args=ap.parse_args()
    result=export(args.checkpoint,args.refinement,args.output) if args.checkpoint else json.loads(args.output.read_text())
    plot(result,args.output,args.figures)
    report(result,args.output.with_name(f'{args.output.stem}_report.md'))


if __name__=='__main__': main()

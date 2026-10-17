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
    profile_path=output.with_name('synthetic_identifiability_profiles.npz')
    np.savez_compressed(profile_path,**arrays)
    result={k:v for k,v in run.items() if k not in ('pid','config')}
    result['config_file']='analysis/input/identifiability_design.json'
    result['checkpoint_sha256']=study.sha(checkpoint)
    result['profile_file']=profile_path.name; result['profile_sha256']=study.sha(profile_path)
    result['refinement']=verification;result['duration_information']=comparisons;result['paired_schedule_widths']=paired
    result['complete']=len(cells)==len(cfg['tau_s'])*len(cfg['duration_s'])*len(cfg['schedules'])*len(cfg['scenarios'])
    output.write_text(json.dumps(result,separators=(',',':'),allow_nan=False)+'\n')
    with output.with_suffix('.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=run['summary'][0].keys(),lineterminator='\n');writer.writeheader();writer.writerows(run['summary'])
    return result


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
DURATION_SOURCES = ('`analysis/output/synthetic_identifiability.json`, '
                    '`analysis/output/synthetic_identifiability_profiles.npz` and '
                    '`analysis/input/identifiability_design.json`')


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
    hours = [f"{d / 3600:g}" for d in cfg['duration_s']]
    panels = '; '.join(f"({fs.LETTERS[i]}) {words}" for i, (_, words) in enumerate(SCENARIOS))
    return (
        "Synthetic development example, not physical data. Profile likelihood-ratio statistic against "
        "candidate C/G for the first registered draw of each scenario, with the slowest generating heater "
        f"time constant ({max(cfg['tau_s']) / 60:g} min) and repeated power steps: {panels}. "
        f"Record length: {styles_phrase([h + ' h' for h in hours])} Panels share axes. The thin horizontal line "
        f"is the nominal likelihood-ratio cutoff, {cfg['profile_delta_chi2']:.2f}. The dash-dot vertical "
        "line marks the generating heater time constant; in the probe-lag case there is no true "
        f"single-node time constant. Curves are clipped above {PROFILE_YMAX}; the full-range profiles are "
        f"retained. Sources: {DURATION_SOURCES}."
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
        f"{', '.join(f'{d / 3600:g}' for d in cfg['duration_s'][:-1])} and {longest / 3600:g} h and do not "
        f"establish interpolation to an untested schedule.{coincide} Longer observations can narrow sets "
        f"while unmodeled drift defeats coverage: at {longest / 3600:g} h {first} matched gain sets reach "
        f"the search edge, and ambient-excursion coverage is at most {100 * cover_long:g} %. Sources: "
        "`analysis/output/synthetic_identifiability.csv` and `analysis/input/identifiability_design.json`."
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
                       label=f'{d / 3600:g} h') for j, d in enumerate(cfg['duration_s'])]
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
        hours = [d / 3600 for d in cfg['duration_s']]
        for k, ax in enumerate(axs.flat):
            ax.set(xscale='log', ylim=(-.04, 1.04))
            ax.set_xticks(hours, [f'{v:g}' for v in hours])
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
    cfg = json.loads(study.CONFIG.read_text())
    profiles = np.load(output.with_name(result['profile_file']))
    for name, fig, text in (
            ('synthetic_identifiability_profiles.png', profiles_figure(result, profiles, cfg),
             profiles_caption(result, cfg)),
            ('synthetic_identifiability_tradeoffs.png', tradeoffs_figure(result, cfg),
             tradeoffs_caption(result, cfg))):
        fs.save(fig, figures / name)
        plt.close(fig)
        fs.caption_path(figures / name).write_text(text + '\n')


def report(result, path):
    cfg=json.loads(study.CONFIG.read_text()); ref=result['refinement']
    n=cfg['replicates_per_cell']; count=sum(len(c['records']) for c in result['cells'])
    failures=[c for c in ref['cells'] if c['max_start_excess_sse']>1e-6]
    lines=["# Executed synthetic I1 design aid", "",
           f"Executed {len(result['cells'])} scenario cells with {count} synthetic fits. Estimation-only reporting is retained.", "",
           "Source: [numeric result](synthetic_identifiability.json), [all-cell CSV](synthetic_identifiability.csv), "
           "[profile arrays](synthetic_identifiability_profiles.npz). This page is generated from those outputs.", "",
           "## What the calculation supports", "",
           "Power-only interventions identify C/G and eta/G under the single-node model. "
           "Jointly scaling C, G and eta leaves the trajectory invariant. "
           "The [derivation and registration](../identifiability_design.md) explain which independent heat-path input would fix the scale.", "",
           "Longer records usually reduce open profiles in the matched scenarios. "
           "The isolated power block gives narrower gain sets than the repeated schedule in the matched cells where both sets close. "
           "This compares equal energy and duration under these assumed response/noise conditions; it does not remove the physical protocol's replication and counterbalancing requirement.", "",
           "Ambient mismatch can produce narrow sets with poor coverage. Extra probe lag also biases the single-node interpretation. "
           "A small residual variance alone does not establish an adequate thermal structure. "
           "No physical detection limit, preferred enclosure or calibration-transfer performance follows from this study.", "",
           "## Slow-response comparison", "",
           f"Generating heater time constant: {max(cfg['tau_s'])/60:g} min. "
           "Every registered duration and schedule is shown for this slice; other time constants remain in the CSV. "
           "Open means a profile set reaches the registered search boundary. Coverage uses all draws, including open sets.", "",
           "| Scenario | Duration [h] | Schedule | Gain coverage [%] | Gain open [%] | Time-constant open [%] |",
           "| --- | ---: | --- | ---: | ---: | ---: |"]
    for r in result['summary']:
        if r['tau_s']==max(cfg['tau_s']):
            lines.append(f"| {r['scenario'].replace('_',' ')} | {r['duration_s']/3600:g} | {r['schedule'].replace('_',' ')} | {100*r['gain_coverage']:.1f} | {100*r['gain_open_fraction']:.1f} | {100*r['tau_open_fraction']:.1f} |")
    lines += ["", "## Profiles and schedule tradeoffs", "",
              "![Profile likelihood-ratio curves for 0.5, 2 and 6 h records in four synthetic scenarios, with the nominal cutoff and generating time constant](../figures/synthetic_identifiability_profiles.png)", "",
              profiles_caption(result, cfg), "",
              "[Caption](../figures/synthetic_identifiability_profiles.caption.md) · "
              "[Vector profiles](../figures/synthetic_identifiability_profiles.svg).", "",
              "![Gain-set openness under matched dynamics and gain coverage under an ambient excursion, by observation duration and schedule](../figures/synthetic_identifiability_tradeoffs.png)", "",
              tradeoffs_caption(result, cfg), "",
              "[Caption](../figures/synthetic_identifiability_tradeoffs.caption.md) · "
              "[Vector tradeoffs](../figures/synthetic_identifiability_tradeoffs.svg).", "",
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
    report(result,args.output.with_name('synthetic_identifiability_report.md'))


if __name__=='__main__': main()

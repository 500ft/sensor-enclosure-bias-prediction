"""Export compact results and render the synthetic design aid from its checkpoint."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from analysis import figure_style as fs
from analysis import synthetic_identifiability as study
import matplotlib.pyplot as plt
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
        writer=csv.DictWriter(f,fieldnames=run['summary'][0].keys());writer.writeheader();writer.writerows(run['summary'])
    return result


def plot(result, output, figures):
    cfg=json.loads(study.CONFIG.read_text()); profiles=np.load(output.with_name(result['profile_file']))
    scenario_titles={'matched':'Matched dynamics + quantization','noisy':'Higher noise + coarser quantization',
                     'ambient_mismatch':'Unobserved ambient excursion','probe_lag':'Additional probe lag'}
    colors=['#2980b9','#e69f00','#882255'];markers=['o','s','^'];styles=['-','--',':']
    with fs.style():
        fig,axs=plt.subplots(2,2,figsize=(8.6,6.5),layout='constrained')
        for ax,(scenario,title) in zip(axs.flat,scenario_titles.items()):
            for j,duration in enumerate(cfg['duration_s']):
                idx=next(i for i,c in enumerate(result['cells']) if c['scenario']==scenario and c['tau_s']==max(cfg['tau_s']) and c['duration_s']==duration and c['schedule']=='repeated_steps')
                ax.plot(profiles[f'cell{idx}_tau_s']/60,profiles[f'cell{idx}_delta_sse'],color=colors[j],ls=styles[j],marker=markers[j],markevery=130,ms=3,label=f'{duration/3600:g} h')
            ax.axhline(cfg['profile_delta_chi2'],color='black',ls='--',lw=.8,label='Nominal LR cutoff')
            ax.axvline(max(cfg['tau_s'])/60,color=fs.ZERO_COLOR,ls=':',lw=.8)
            ax.set(xscale='log',ylim=(0,12),xlabel='Candidate C/G [min]',ylabel='Profile likelihood-ratio statistic',title=title)
            fs.grid_y(ax)
        handles,labels=axs.flat[0].get_legend_handles_labels()
        fig.legend(handles,labels,loc='outside lower center',ncol=4)
        fig.suptitle('Synthetic profiles: repeated steps, first registered draw\nDotted vertical line: generating heater time constant; curves clipped above display range',fontsize=10)
        fs.save(fig,figures/'synthetic_identifiability_profiles.png');plt.close(fig)
        fig,axs=plt.subplots(2,3,figsize=(9.5,6),layout='constrained')
        for col,tau in enumerate(cfg['tau_s']):
            for j,sch in enumerate(cfg['schedules']):
                matched=sorted([r for r in result['summary'] if r['scenario']=='matched' and r['tau_s']==tau and r['schedule']==sch],key=lambda r:r['duration_s'])
                mismatch=sorted([r for r in result['summary'] if r['scenario']=='ambient_mismatch' and r['tau_s']==tau and r['schedule']==sch],key=lambda r:r['duration_s'])
                x=[r['duration_s']/3600 for r in matched]
                # Bounded domain widths can look precise when a set reaches its search edge.
                # Plot openness directly instead of hiding it in a finite width.
                axs[0,col].plot(x,[r['gain_open_fraction'] for r in matched],marker=markers[j],ls=styles[j],color=colors[j],label=sch.replace('_',' '))
                axs[1,col].plot(x,[r['gain_coverage'] for r in mismatch],marker=markers[j],ls=styles[j],color=colors[j])
            axs[0,col].set_title(f'Generating C/G = {tau/60:g} min')
            axs[1,col].axhline(cfg['profile_level'],color=fs.ZERO_COLOR,ls=':',lw=.9)
            for row in range(2):
                axs[row,col].set(xscale='log',xticks=x,xticklabels=[f'{v:g}' for v in x],ylim=(-.03,1.03),xlabel='Observation duration [h]')
                axs[row,col].xaxis.set_minor_formatter(NullFormatter())
                fs.grid_y(axs[row,col])
        axs[0,0].set_ylabel('Gain sets reaching search edge\nMatched dynamics [fraction]')
        axs[1,0].set_ylabel('Gain sets containing true eta/G\nAmbient mismatch [fraction]')
        fig.legend(*axs[0,0].get_legend_handles_labels(),loc='outside lower center',ncol=2)
        fig.suptitle('Synthetic schedule tradeoff at equal energy\nLonger observations can narrow sets while unmodeled drift defeats coverage',fontsize=10)
        fs.save(fig,figures/'synthetic_identifiability_tradeoffs.png');plt.close(fig)


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
              "![Profile likelihood curves by assumed duration for each noise and model scenario](../figures/synthetic_identifiability_profiles.png)", "",
              "[Vector profiles](../figures/synthetic_identifiability_profiles.svg). First registered draw, slow-response case and repeated steps throughout. "
              "The vertical line marks the generating heater constant. In the probe-lag case there is no true single-node time constant. "
              "All full-range profiles are retained; the figure clips high likelihood-ratio values for readability.", "",
              "![Matched-model gain openness and ambient-mismatch gain coverage by observation duration and schedule](../figures/synthetic_identifiability_tradeoffs.png)", "",
              "[Vector tradeoffs](../figures/synthetic_identifiability_tradeoffs.svg). The dotted coverage reference is nominal, not a measured performance target. "
              "Lines connect discrete scenarios and do not establish interpolation to an untested schedule.", "",
              "The JSON duration_information entries give paired log width reduction relative to the shortest same-schedule record. "
              "paired_schedule_widths compares single versus repeated steps. Positive values mean narrower repeated-step sets. "
              "These are descriptive information proxies, not Bayesian information or entropy. Only pairs with both sets closed contribute; their counts are reported. "
              "Null means no eligible pair. They must be read alongside openness and coverage, rather than used to rank schedules alone.", "",
              "## Numerical validation and resource use", "",
              f"The refinement doubled profile-grid resolution to {ref['refined_grid_count']} points on the same draws. "
              f"Time-constant coverage changed in {ref['tau_coverage_changes']} fits and gain coverage in {ref['gain_coverage_changes']} fits. "
              f"Maximum relative estimate changes were {100*ref['max_tau_hat_relative_change']:.2f}% for time constant and {100*ref['max_gain_hat_relative_change']:.2f}% for gain. "
              "Grid agreement on coverage does not prove continuous optimization accuracy or calibrated uncertainty.", "",
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

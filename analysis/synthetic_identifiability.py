"""Development-only I1 identifiability study. No field data or rig qualification.

Run with OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1.
See identifiability_design.md and input/identifiability_design.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import resource
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'analysis/input/identifiability_design.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def schedule(duration, dt, levels, amplitude):
    # Insert every transition, even when duration/8 is not divisible by cadence.
    t = np.unique(np.r_[np.arange(0, duration, dt), np.linspace(0, duration, len(levels)+1)])
    p = amplitude * np.asarray(levels)[np.minimum((t[:-1]*len(levels)/duration).astype(int), len(levels)-1)]
    return t, p


def generate(t, p, ambient, tau, beta, initial=0., lag=0.):
    """Exact state recurrence, ambient piecewise linear, power on [t_i,t_i+1)."""
    out = np.empty(len(t))
    if lag == 0:
        x = initial
        out[0] = x
        for i, dt in enumerate(np.diff(t)):
            slope = (ambient[i+1]-ambient[i])/dt
            eq = beta*p[i]-tau*slope
            x = eq+(x-eq)*np.exp(-dt/tau)
            out[i+1] = x
    else:
        # Heated body followed by a negligible-loading probe: two physical states.
        a = np.array([[-1/tau, 0], [1/lag, -1/lag]])
        val, vec = np.linalg.eig(a)
        val, vec = val.real, vec.real
        inv = np.linalg.inv(vec)
        transitions = {dt: (vec*np.exp(val*dt))@inv for dt in np.unique(np.diff(t))}
        x = np.full(2, initial)
        out[0] = x[1]
        for i, dt in enumerate(np.diff(t)):
            slope = (ambient[i+1]-ambient[i])/dt
            u = np.array([beta*p[i]/tau-slope, -slope])
            eq = -np.linalg.solve(a, u)
            x = eq+transitions[dt]@(x-eq)
            out[i+1] = x[1]
    return out+ambient


def step_basis(t, p, taus):
    """Independent analytical superposition of steps, not generator recurrence."""
    taus = np.asarray(taus)
    response = np.zeros((len(taus), len(t)))
    changes = np.diff(np.r_[0., p])
    for ti, delta in zip(t[:-1], changes):
        if delta:
            elapsed = np.maximum(t-ti, 0)
            response += delta*(-np.expm1(-elapsed[None, :]/taus[:, None]))
    return response


def whiten(x, sigma, rho):
    y = np.array(x, dtype=float, copy=True)
    y[..., 0] = x[..., 0]/sigma
    y[..., 1:] = (x[..., 1:]-rho*x[..., :-1])/(sigma*np.sqrt(1-rho*rho))
    return y


def fit_bank(t, p, taus, sigma, rho, ambient_slope):
    n = len(t)
    e = np.exp(-t[None, :]/taus[:, None])
    nuisance = np.stack([np.ones_like(e), e, np.broadcast_to(t/t[-1], e.shape)], axis=-1)
    # Whiten time axis, then QR removes nuisance coefficients without normal equations.
    nuisance = whiten(nuisance.transpose(0, 2, 1), sigma, rho).transpose(0, 2, 1)
    q, _ = np.linalg.qr(nuisance, mode='reduced')
    x = whiten(step_basis(t, p, taus), sigma, rho)
    x -= np.einsum('gnj,gj->gn', q, np.einsum('gnj,gn->gj', q, x))
    ambient = whiten(-ambient_slope*taus[:, None]*(1-e), sigma, rho)
    a = np.sum(x*x, axis=1)
    if np.any(a < 1e-16):
        raise ValueError('power response fully confounded with nuisance terms')
    return q, x, a, ambient


def profile(bank, observations, sigma, rho, bounds):
    q, x, a, ambient = bank
    y = whiten(observations.T, sigma, rho).T
    qty = np.einsum('gnj,nr->gjr', q, y)
    qta = np.einsum('gnj,gn->gj', q, ambient)
    norm = (np.sum(y*y, axis=0)[None, :] - 2*ambient@y
            + np.sum(ambient*ambient, axis=1)[:, None]
            - np.sum((qty-qta[:, :, None])**2, axis=1))
    xy = x@y-np.sum(x*ambient, axis=1)[:, None]
    free = xy/a[:, None]
    beta = np.clip(free, *bounds)
    sse = norm-2*beta*xy+beta*beta*a[:, None]
    if np.min(sse) < -1e-6:
        raise ValueError('negative residual norm beyond roundoff')
    return np.maximum(sse, 0), free, norm-xy*xy/a[:, None]


def segments(grid, values, cutoff, log=False):
    """Connected profile sets, interpolated crossings; search edges stay open."""
    z = np.log(grid) if log else grid
    good = values <= cutoff
    groups = np.split(np.flatnonzero(good), np.flatnonzero(np.diff(np.flatnonzero(good)) > 1)+1)
    output = []
    for g in groups:
        if not len(g):
            continue
        lo, hi = int(g[0]), int(g[-1])
        left = z[lo] if lo == 0 else np.interp(cutoff, [values[lo], values[lo-1]], [z[lo], z[lo-1]])
        right = z[hi] if hi == len(z)-1 else np.interp(cutoff, [values[hi], values[hi+1]], [z[hi], z[hi+1]])
        output.append({'low': float(np.exp(left) if log else left),
                       'high': float(np.exp(right) if log else right),
                       'open_low': lo == 0, 'open_high': hi == len(z)-1})
    return output


def gain_sets(a, free, free_sse, cutoff, bounds):
    """Union of exact conditional quadratic sets over sampled tau values."""
    valid = free_sse <= cutoff
    radii = np.sqrt(np.maximum(0, (cutoff-free_sse[valid])/a[valid]))
    intervals = sorted((max(bounds[0], b-r), min(bounds[1], b+r))
                       for b, r in zip(free[valid], radii) if b+r >= bounds[0] and b-r <= bounds[1])
    merged = []
    for lo, hi in intervals:
        if merged and lo <= merged[-1][1]:
            merged[-1][1] = max(hi, merged[-1][1])
        else:
            merged.append([lo, hi])
    return [{'low': float(lo), 'high': float(hi), 'open_low': bool(lo == bounds[0]),
             'open_high': bool(hi == bounds[1])} for lo, hi in merged]


def contains(intervals, value):
    return any(s['low'] <= value <= s['high'] for s in intervals)


def grid_starts(values, taus, starts):
    # Multiple starts on the discrete profile, not an optimizer claim in R^3.
    ends = []
    for start in starts:
        i = int(np.argmin(abs(np.log(taus/start))))
        while True:
            candidates = [j for j in (i-1, i, i+1) if 0 <= j < len(values)]
            j = min(candidates, key=lambda k: values[k])
            if j == i:
                break
            i = j
        ends.append({'tau_s': float(taus[i]), 'delta_sse': float(values[i]-min(values))})
    return ends


def cell(config, scenario_name, tau, duration, schedule_name, grid_count=None):
    sc = config['scenarios'][scenario_name]
    t, p = schedule(duration, config['dt_s'], config['schedules'][schedule_name], config['power_w'])
    nrep = config['replicates_per_cell']
    # Explicit stable seed independent of duration/schedule; repeat streams enable pairing.
    seed = [config['seed'], list(config['scenarios']).index(scenario_name), config['tau_s'].index(tau)]
    rng = np.random.default_rng(np.random.SeedSequence(seed))
    eta = rng.uniform(*config['coupling_uniform'], nrep)
    beta = eta/config['conductance_w_per_k']
    initial = rng.normal(0, config['initial_offset_sd_k'], nrep)
    offsets = rng.normal(0, config['calibration_offset_sd_k'], nrep)
    phase = rng.uniform(0, 2*np.pi, nrep)
    slope = config['ambient_ramp_k_per_hour']/3600
    ambient = slope*t
    y = np.empty((len(t), nrep))
    # Draw fixed maximum stream before selecting cadence nodes for comparable durations.
    max_duration = max(config['duration_s'])
    for j in range(nrep):
        noise_rng = np.random.default_rng(np.random.SeedSequence(seed+[j, 1]))
        innovations = noise_rng.normal(size=int(max_duration/config['dt_s'])+1)
        noise = np.empty_like(innovations)
        noise[0] = sc['sigma_k']*innovations[0]
        for k in range(1, len(noise)):
            noise[k] = sc['rho']*noise[k-1]+sc['sigma_k']*np.sqrt(1-sc['rho']**2)*innovations[k]
        # All registered boundaries align with dt; other inputs must not silently alias.
        if not np.allclose(t/config['dt_s'], np.round(t/config['dt_s'])):
            raise ValueError('registered sampling grid must align with schedule transitions')
        actual_ambient = ambient+sc['unobserved_ambient_k']*(np.sin(2*np.pi*t/duration+phase[j])-np.sin(phase[j]))
        clean = generate(t, p, actual_ambient, tau, beta[j], initial[j], sc['probe_lag_fraction']*tau)
        measured = clean+offsets[j]+noise[np.round(t/config['dt_s']).astype(int)]
        y[:, j] = sc['quantum_k']*np.round(measured/sc['quantum_k'])-ambient
    taus = np.unique(np.r_[np.geomspace(*config['tau_search_s'], grid_count or config['tau_grid_count']), tau])
    bank = fit_bank(t, p, taus, sc['sigma_k'], sc['rho'], slope)
    sse, free, free_sse = profile(bank, y, sc['sigma_k'], sc['rho'], config['gain_search_k_per_w'])
    records = []
    for j in range(nrep):
        best = int(np.argmin(sse[:, j]))
        cutoff = float(sse[best, j]+config['profile_delta_chi2'])
        ts = segments(taus, sse[:, j], cutoff, log=True)
        bs = gain_sets(bank[2], free[:, j], free_sse[:, j], cutoff, config['gain_search_k_per_w'])
        records.append({'replicate': j, 'eta': float(eta[j]), 'gain_true_k_per_w': float(beta[j]),
                        'tau_hat_s': float(taus[best]), 'gain_hat_k_per_w': float(np.clip(free[best, j], *config['gain_search_k_per_w'])),
                        'tau_sets_s': ts, 'gain_sets_k_per_w': bs,
                        'tau_generating_value_in_set': contains(ts, tau), 'gain_covered': contains(bs, beta[j]),
                        'sse': float(sse[best, j]), 'residual_dof': len(t)-5})
    # A complete first-replicate profile is retained for every cell, not chosen by outcome.
    example = {'replicate': 0, 'tau_s': taus.tolist(), 'delta_sse': (sse[:, 0]-min(sse[:, 0])).tolist(),
               'gain_profile_k_per_w': np.clip(free[:, 0], *config['gain_search_k_per_w']).tolist(),
               'starts': grid_starts(sse[:, 0], taus, config['multiple_start_tau_s'])}
    key = f'{scenario_name}__tau{tau}__duration{duration}__{schedule_name}'
    meta = {'key': key, 'scenario': scenario_name, 'tau_s': tau, 'duration_s': duration,
            'schedule': schedule_name, 'seed_sequence': seed, 'samples': len(t),
            'input_energy_j': float(np.sum(p*np.diff(t))), 'records': records, 'profile': example}
    return meta, {'time_s': t, 'power_w': p, 'observed_delta_k': y}


def validation():
    t = np.arange(0, 2401, 10.)
    p = np.where((t[:-1] >= 300) & (t[:-1] < 1500), .5, 0.)
    tau, beta, initial = 600., 3., .2
    ambient = t*.0001
    exact = generate(t, p, ambient, tau, beta, initial)
    algebra = ambient + beta*step_basis(t, p, np.array([tau]))[0] - tau*.0001*(1-np.exp(-t/tau)) + initial*np.exp(-t/tau)
    max_algebra = float(np.max(abs(exact-algebra)))
    # Independently integrated two-state physical ODE using substepped RK4.
    errors = []
    for lag in (0., tau/2):
        x = np.array([initial, initial])
        values = [x[1]]
        def rhs(state, power):
            body = (beta*power-state[0])/tau-.0001
            probe = body if lag == 0 else (state[0]-state[1])/lag-.0001
            return np.array([body, probe])
        for power in p:
            for _ in range(10):
                k1 = rhs(x, power); k2 = rhs(x+k1/2, power)
                k3 = rhs(x+k2/2, power); k4 = rhs(x+k3, power)
                x += (k1+2*k2+2*k3+k4)/6
            values.append(x[1])
        errors.append(float(np.max(abs(np.array(values)+ambient-generate(t,p,ambient,tau,beta,initial,lag)))))
    # Exact interval energy: C dtheta = eta P dt - G integral(theta) - C dTa.
    c, g, eta = 120., .2, .6
    theta = exact-ambient
    dt = np.diff(t); eq = beta*p-tau*.0001
    integral = eq*dt+(theta[:-1]-eq)*tau*(-np.expm1(-dt/tau))
    energy = c*np.diff(theta)-eta*p*dt+g*integral+c*np.diff(ambient)
    # Independent physical-parameter RK4 scaling for several nontrivial waveforms.
    scaling = []
    for factor in (.25, 1., 1.5):
        x = initial; out = [x]
        for power in p:
            def f(v): return (factor*eta*power-factor*g*v)/(factor*c)-.0001
            for _ in range(10):
                a=f(x); b=f(x+a/2); cc=f(x+b/2); d=f(x+cc)
                x+=(a+2*b+2*cc+d)/6
            out.append(x)
        scaling.append(float(np.max(abs(np.array(out)-theta))))
    # Whitening agrees with the direct stationary AR(1) precision form.
    rng=np.random.default_rng(4); z=rng.normal(size=11); rho=.8; sigma=.04
    covariance=sigma**2*rho**abs(np.arange(11)[:,None]-np.arange(11)[None,:])
    whitening_error=abs(float(np.sum(whiten(z,sigma,rho)**2)-z@np.linalg.solve(covariance,z)))
    assert max_algebra < 1e-11 and max(errors+scaling) < 1e-9
    assert max(abs(energy)) < 1e-10 and whitening_error < 1e-8
    return {'closed_form_max_k': max_algebra, 'rk4_max_k': errors, 'scaled_physical_rk4_max_k': scaling,
            'interval_energy_max_j': float(max(abs(energy))), 'whitening_quadratic_error': whitening_error}


def summarize(cells):
    rows=[]
    for c in cells:
        rr=c['records']; n=len(rr)
        row={k:c[k] for k in ('key','scenario','tau_s','duration_s','schedule','samples','input_energy_j')}
        row['replicates']=n
        for name, field, truth in [('tau','tau_sets_s',c['tau_s']), ('gain','gain_sets_k_per_w',None)]:
            row[name+'_open_fraction']=sum(any(s['open_low'] or s['open_high'] for s in r[field]) for r in rr)/n
            row[name+'_disconnected_fraction']=sum(len(r[field])>1 for r in rr)/n
            cover='tau_generating_value_in_set' if name=='tau' else 'gain_covered'
            row[name+'_coverage']=sum(r[cover] for r in rr)/n
            # Report finite-domain width separately from openness; open sets are truncated.
            width=float(np.median([sum(np.log(s['high']/s['low']) if s['low']>0 else np.inf for s in r[field]) for r in rr]))
            row[name+'_median_domain_log_width']=width if np.isfinite(width) else None
            hat='tau_hat_s' if name=='tau' else 'gain_hat_k_per_w'
            row[name+'_median_relative_error']=float(np.median([(r[hat]/(truth or r['gain_true_k_per_w'])-1) for r in rr]))
        row['median_reduced_sse']=float(np.median([r['sse']/r['residual_dof'] for r in rr]))
        rows.append(row)
    return rows


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--raw',type=Path,required=True)
    ap.add_argument('--max-cells',type=int)
    ap.add_argument('--resume',action='store_true')
    args=ap.parse_args()
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):
        if os.environ.get(key)!='1':
            raise SystemExit(f'set {key}=1 before launching this process')
    config=json.loads(CONFIG.read_text()); start=time.monotonic()
    checks=validation()
    args.out.mkdir(parents=True,exist_ok=True); args.raw.mkdir(parents=True,exist_ok=True)
    checkpoint=args.out/'identifiability_checkpoint.json'
    cells=[]; previous_elapsed=0.
    if args.resume and checkpoint.exists():
        old=json.loads(checkpoint.read_text())
        if old['config_sha256']!=sha(CONFIG) or old['generator_sha256']!=sha(__file__):
            raise SystemExit('checkpoint inputs differ; preserve old run and use a new output directory')
        cells=old['cells'];previous_elapsed=old['elapsed_s']
    done={c['key'] for c in cells}
    for sc in config['scenarios']:
        for tau in config['tau_s']:
            for duration in config['duration_s']:
                for sch in config['schedules']:
                    key=f'{sc}__tau{tau}__duration{duration}__{sch}'
                    if key in done: continue
                    if args.max_cells and len(cells)>=args.max_cells: break
                    if previous_elapsed+time.monotonic()-start>=config['maximum_runtime_s']: break
                    c,raw=cell(config,sc,tau,duration,sch)
                    path=args.raw/(key+'.npz');np.savez_compressed(path,**raw)
                    c['raw_sha256']=sha(path); c['raw_file']=path.name
                    cells.append(c)
                    total_bytes=sum(p.stat().st_size for p in args.raw.glob('*.npz'))
                    record={'status':'executed synthetic development only','config_sha256':sha(CONFIG),'generator_sha256':sha(__file__),
                            'config':config,'validation':checks,'cells':cells,'summary':summarize(cells),
                            'elapsed_s':previous_elapsed+time.monotonic()-start,'raw_bytes':total_bytes,
                            'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if platform.system()=='Darwin' else 1024),
                            'python':platform.python_version(),'numpy':np.__version__,'pid':os.getpid(),
                            'threads':{k:os.environ[k] for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS')}}
                    temp=checkpoint.with_suffix('.tmp');temp.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n');temp.replace(checkpoint)
                    print(f'{len(cells)} cells; {key}; {record["elapsed_s"]:.1f} s; RSS {record["peak_rss_bytes"]/2**20:.1f} MiB',flush=True)
                    if total_bytes>config['maximum_artifact_bytes']: raise SystemExit('artifact ceiling reached; checkpoint retained')
    print(checkpoint)


if __name__=='__main__':
    main()

"""Refine the executed profile grid on the same synthetic draws, not new data."""
import argparse
import json
from pathlib import Path
import resource
import platform
import time
import numpy as np
from analysis import synthetic_identifiability as s


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('checkpoint',type=Path);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args(); old=json.loads(args.checkpoint.read_text());cfg=old['config'];start=time.monotonic()
    changes=[]
    for c in old['cells']:
        refined,_=s.cell(cfg,c['scenario'],c['tau_s'],c['duration_s'],c['schedule'],grid_count=2*cfg['tau_grid_count']-1)
        rr=refined['records']; orig=c['records']
        changes.append({'key':c['key'],
                        'max_tau_hat_relative_change':max(abs(a['tau_hat_s']/b['tau_hat_s']-1) for a,b in zip(rr,orig)),
                        'max_gain_hat_relative_change':max(abs(a['gain_hat_k_per_w']-b['gain_hat_k_per_w'])/max(b['gain_hat_k_per_w'],1e-12) for a,b in zip(rr,orig)),
                        'tau_coverage_changes':sum(a['tau_generating_value_in_set']!=b['tau_generating_value_in_set'] for a,b in zip(rr,orig)),
                        'gain_coverage_changes':sum(a['gain_covered']!=b['gain_covered'] for a,b in zip(rr,orig)),
                        'max_start_excess_sse':max(v['delta_sse'] for v in c['profile']['starts'])})
        print(len(changes), c['key'],flush=True)
    result={'checkpoint_sha256':s.sha(args.checkpoint),'generator_sha256':s.sha(s.__file__),
            'verifier_sha256':s.sha(__file__),'refined_grid_count':2*cfg['tau_grid_count']-1,
            'elapsed_s':time.monotonic()-start,
            'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if platform.system()=='Darwin' else 1024),
            'cells':changes,'max_tau_hat_relative_change':max(c['max_tau_hat_relative_change'] for c in changes),
            'max_gain_hat_relative_change':max(c['max_gain_hat_relative_change'] for c in changes),
            'tau_coverage_changes':sum(c['tau_coverage_changes'] for c in changes),
            'gain_coverage_changes':sum(c['gain_coverage_changes'] for c in changes),
            'max_start_excess_sse':max(c['max_start_excess_sse'] for c in changes)}
    args.out.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__': main()

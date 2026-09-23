"""Run the preregistered battery. Stage A: controls only. Stage B: Voynich only.

    python3 -m mechanism.run A      # controls -> results/mechanism/stageA.json
    python3 -m mechanism.run B      # Voynich  -> results/mechanism/stageB.json
"""
import json
import os
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed

OUT = 'results/mechanism'

TOKEN_TESTS = ['t1', 't2c', 't3a', 't3b', 't3c', 't4a', 't4b', 't4c', 't6a', 't7b']


def build(name):
    from mechanism import controls as K
    from mechanism import corpus as C
    if name == 'VOYNICH':
        return C.load_voynich()
    if name == 'GIB':
        return C.load_gibberish()
    if name == 'LATW':
        return C.load_lang_wrapped('LAT')
    if name in C.LANGS:
        return C.load_lang_chunked(name)
    if name == 'MK-sec':
        return K.mk_sec()
    if name == 'MK-page':
        return K.mk_page()
    if name == 'RUGG':
        return K.rugg()
    if name == 'TS':
        return K.ts()
    if name == 'NAIB-lines':
        return K.naib(True)
    if name == 'NAIB-run':
        return K.naib(False)
    if name.startswith('DEV-'):
        _, w, seed = name.split('-')
        return K.dev(float(w), seed=int(seed))
    if name.startswith('DRIFT-'):
        return K.drift(name.split('-')[1])
    raise ValueError(name)


def plan(name):
    if name == 'GIB':
        return ['t1', 't1_nohyph', 't2a_margin', 't2a_para', 't2b', 't2b_nohyph', 't2c', 't3a', 't3b', 't3c',
                't4a', 't4b', 't4c', 't6a']
    if name == 'LATW':
        return ['t1', 't2a_margin', 't2b', 't2c']
    if name.startswith('DEV-'):
        # seed 0 also enters T6a as a stationary procedure (PREREG T6a)
        return ['t4a', 't4b', 't4c'] + (['t6a'] if name.endswith('-0') else [])
    if name.startswith('DRIFT-'):
        return ['t5']
    if name == 'VOYNICH':
        return ['t1', 't2a_margin', 't2a_para', 't2b', 't2c', 't3a', 't3a_full', 't3b', 't3c', 't4a', 't4b', 't4c',
                't5', 't6a', 't6c', 't7a', 't7b']
    extra = ['t3a_full'] if name in ('LAT', 'LATV', 'ITA', 'GER', 'ENG') else []
    t5 = ['t5'] if name in ('MK-sec', 'MK-page', 'TS', 'NAIB-run', 'LAT') else []
    return TOKEN_TESTS + extra + t5


def run_test(c, t):
    from mechanism import tests as T
    if t == 't1':
        return T.t1(c)
    if t == 't1_nohyph':
        return T.t1(c, drop_hyph=True)
    if t == 't2a_margin':
        return T.t2a(c, 'margin')
    if t == 't2a_para':
        return T.t2a(c, 'para')
    if t in ('t2b', 't2b_nohyph'):
        filt = (lambda p: p.section == 'S') if c.name == 'VOYNICH' else (lambda p: True)
        return T.t2b(c, filt, drop_hyph=(t == 't2b_nohyph'))
    if t == 't2c':
        return T.t2c(c)
    if t == 't3a':
        return T.t3a(c)
    if t == 't3a_full':
        r = {'all': T.t3a_full(c)}
        if c.name == 'VOYNICH':
            for h in sorted({p.hand for p in c.pages if p.hand}):
                r['hand' + h] = T.t3a_full(c, hand=h)
        return r
    if t == 't3b':
        return T.t3b(c)
    if t == 't3c':
        return T.t3c(c)
    if t == 't4a':
        return T.t4a(c)
    if t == 't4b':
        return T.t4b(c)
    if t == 't4c':
        return T.t4c(c)
    if t == 't5':
        return T.t5(c)
    if t == 't6a':
        return T.t6a(c)
    if t == 't6c':
        return T.t6c(c, None)
    if t == 't7a':
        return T.t7a()
    if t == 't7b':
        return T.t7b(c, double_coded_only=(c.name == 'VOYNICH'))
    raise ValueError(t)


def job(name):
    # Apple Accelerate BLAS emits spurious floating-point warnings in matmul (numpy 2.0); results verified finite
    warnings.filterwarnings('ignore', category=RuntimeWarning, message='.*encountered in matmul')
    t0 = time.time()
    c = build(name)
    res = {'_meta': {'class': c.gclass, 'note': c.note, 'tokens': c.ntok(), 'pages': len(c.pages)}}
    for t in plan(name):
        t1 = time.time()
        try:
            res[t] = run_test(c, t)
        except Exception as e:  # recorded, not hidden
            res[t] = {'error': repr(e)}
        res[t + '_sec'] = round(time.time() - t1, 1)
    res['_meta']['seconds'] = round(time.time() - t0, 1)
    return name, res


def main(stage, only=None):
    os.makedirs(OUT, exist_ok=True)
    if stage == 'A':
        names = ['GIB', 'LATW', 'LAT', 'LATV', 'ITA', 'GER', 'ENG', 'MK-sec', 'MK-page', 'RUGG', 'TS',
                 'NAIB-lines', 'NAIB-run', 'DRIFT-smooth', 'DRIFT-step']
        names += [f'DEV-{w}-{s}' for w in ('0.1', '0.2', '0.4') for s in range(10)]
    else:
        names = ['VOYNICH']
    if only:
        names = [n for n in names if n in only]
    path = f'{OUT}/stage{stage}.json'
    results = json.load(open(path)) if (only and os.path.exists(path)) else {}
    with ProcessPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(job, n): n for n in names}
        for f in as_completed(futs):
            n, r = f.result()
            results[n] = r
            print(n, r['_meta'], flush=True)
            json.dump(results, open(path, 'w'), indent=1, default=float)
    print('written', path)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:] or None)

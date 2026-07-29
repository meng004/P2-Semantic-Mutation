# DOSE_CALIBRATION — EXP-DOSE F-10 two-axis ledger

Freeze seed: `20260728`. Design: 6 levels × 20 repeats × 8 curves = 960.

## eps_tol provenance

`data/mr_export/{put}_MP{1|3}_mr.json` contains **no** `eps_tol` / `epsilon` field (keys: put, mp, r_name, R_name, primary, sample_pairs). Per-curve `eps_tol` is taken from the numeric threshold of the aligned `R_mp` predicate in `src/p2/mrs/{put}.py` (or a documented normalized/surrogate scale when the predicate is a hard bound / envelope). The mr_export file is retained for put/mp/r_name/R_name provenance.

## Direct invariant-violation functionals (F-10; not MR checkers)

| Curve | Functional V | Formula |
|---|---|---|
| CE-A1 | conservation-drift | mean_x |y_mut(x)-y_orig(x)| on PROBE_X |
| CE-B3 | linearity-violation | mean_x | |y(x+0.1)-y(x)| - 0.1 | |
| CE-C1 | anti-symmetry residual | mean_x |y(x)+y(1-x)| |
| CE-D3 | probability bias | mean_x |p_mut(x)-p_orig(x)| |
| HP-A1 | relative accuracy loss | mean_x |y_mut-y_ref|/(1+|y_ref|) |
| HP-B3 | analytic residual | mean_x |y(x)-(x+1/3)| |
| HP-C1 | analytic residual | mean_x |y(x)-erf(6x-3)| |
| HP-D3 | calibration drift | mean_x |p_mut(x)-p_orig(x)| |

## Nominal → realized two-axis table (mean over 20 seeded instances)

### CE-A1

- eps_tol = `1.0`
- eps_tol source: src/p2/mrs/a1.py R_mp1 uses guard abs(y+y')<1e6 (not a continuous violation scale). Direct functional V = mean |y_mut(x)-y_orig(x)| on PROBE_X; eps_tol:=1.0 is the unit of that functional (normalized detection scale; matches power_report 'eps_tol normalised 1.0').
- window: delta_r=`0`, eta_bar=`1e-06`, halfwidth=`2e-06`

| level | nominal_amp | target eps_m | realized mean eps_m | realized/eps_tol |
|---|---|---|---|---|
| e1 | 0.00411118 | 0.25 | 0.250526 | 0.2505 |
| e2 | 0.0066052 | 0.435275 | 0.438172 | 0.4382 |
| e3 | 0.0108877 | 0.757858 | 0.749268 | 0.7493 |
| e4 | 0.0193812 | 1.31951 | 1.32379 | 1.3238 |
| e5 | 0.0428977 | 2.2974 | 2.30385 | 2.3039 |
| e6 | 6.60141 | 4 | 3.99528 | 3.9953 |

### CE-B3

- eps_tol = `0.02`
- eps_tol source: src/p2/mrs/b3.py R_mp1: abs(abs(y_new-y_orig)-0.1) < 0.02 → continuous tol 0.02 on the linearity residual.
- window: delta_r=`1.14106e-16`, eta_bar=`0.00843374`, halfwidth=`0.0168675`

| level | nominal_amp | target eps_m | realized mean eps_m | realized/eps_tol |
|---|---|---|---|---|
| e1 | 0.0482303 | 0.005 | 0.00503894 | 0.2519 |
| e2 | 0.0821308 | 0.00870551 | 0.00865836 | 0.4329 |
| e3 | 0.142205 | 0.0151572 | 0.0150027 | 0.7501 |
| e4 | 0.250352 | 0.0263902 | 0.0260563 | 1.3028 |
| e5 | 0.433472 | 0.0459479 | 0.0458525 | 2.2926 |
| e6 | 0.763125 | 0.08 | 0.0804458 | 4.0223 |

### CE-C1

- eps_tol = `0.1`
- eps_tol source: src/p2/mrs/c1.py R_mp1: abs(y+y') < 0.1 → tol 0.1 on anti-symmetry residual.
- window: delta_r=`0.000260411`, eta_bar=`1e-06`, halfwidth=`0.000262411`

| level | nominal_amp | target eps_m | realized mean eps_m | realized/eps_tol |
|---|---|---|---|---|
| e1 | 0.0126346 | 0.025 | 0.0250078 | 0.2501 |
| e2 | 0.0219683 | 0.0435275 | 0.0437501 | 0.4375 |
| e3 | 0.0381972 | 0.0757858 | 0.0763663 | 0.7637 |
| e4 | 0.0655249 | 0.131951 | 0.130892 | 1.3089 |
| e5 | 0.113931 | 0.22974 | 0.226356 | 2.2636 |
| e6 | 0.200786 | 0.4 | 0.400474 | 4.0047 |

### CE-D3

- eps_tol = `0.05`
- eps_tol source: src/p2/mrs/d3.py R_mp1 is a hard bound y in [0,1] (no continuous tol). Surrogate soft margin 0.05 matches MP2/MP5 slack in the same module; functional V = mean |bias| = mean |p_mut - p_orig|.
- window: delta_r=`0`, eta_bar=`1e-06`, halfwidth=`2e-06`

| level | nominal_amp | target eps_m | realized mean eps_m | realized/eps_tol |
|---|---|---|---|---|
| e1 | 0.0124653 | 0.0125 | 0.0124683 | 0.2494 |
| e2 | 0.0219683 | 0.0217638 | 0.0219743 | 0.4395 |
| e3 | 0.0376853 | 0.0378929 | 0.0377773 | 0.7555 |
| e4 | 0.0664149 | 0.0659754 | 0.0660649 | 1.3213 |
| e5 | 0.115478 | 0.11487 | 0.114366 | 2.2873 |
| e6 | 0.200786 | 0.2 | 0.202483 | 4.0497 |

### HP-A1

- eps_tol = `1.0`
- eps_tol source: src/p2/mrs/a1.py R_mp3 is an attractor-envelope predicate (bound 60), not a continuous accuracy tol. Direct functional V = mean |y_loose(x)-y_ref(x)| / (1+|y_ref|) vs high-fidelity ref; eps_tol:=1.0 (normalized detection scale).
- window: delta_r=`0`, eta_bar=`1e-06`, halfwidth=`2e-06`

| level | nominal_amp | target eps_m | realized mean eps_m | realized/eps_tol |
|---|---|---|---|---|
| e1 | 4.61932 | 0.25 | 0.287366 | 0.2874 |
| e2 | 4.84068 | 0.435275 | 0.410563 | 0.4106 |
| e3 | 5.07266 | 0.757858 | 0.685801 | 0.6858 |
| e4 | 5.37831 | 1.31951 | 1.37954 | 1.3795 |
| e5 | 5.70239 | 2.2974 | 2.03868 | 2.0387 |
| e6 | 6.4103 | 4 | 3.90429 | 3.9043 |

### HP-B3

- eps_tol = `0.05`
- eps_tol source: src/p2/mrs/b3.py R_mp3 envelope slack 0.05 around analytic integral.
- window: delta_r=`0.00447051`, eta_bar=`0.00843374`, halfwidth=`0.021338`

| level | nominal_amp | target eps_m | realized mean eps_m | realized/eps_tol |
|---|---|---|---|---|
| e1 | 3.302 | 0.0125 | 0.0132676 | 0.2654 |
| e2 | 4.53782 | 0.0217638 | 0.0281018 | 0.5620 |
| e3 | 4.71076 | 0.0378929 | 0.0318601 | 0.6372 |
| e4 | 4.98261 | 0.0659754 | 0.0592268 | 1.1845 |
| e5 | 6.12063 | 0.11487 | 0.120213 | 2.4043 |
| e6 | 8.5 | 0.2 | 0.245355 | 4.9071 |

### HP-C1

- eps_tol = `0.1`
- eps_tol source: src/p2/mrs/c1.py R_mp3 overfit margin 0.1 beyond target range [-1,1].
- window: delta_r=`0.00033665`, eta_bar=`1e-06`, halfwidth=`0.00033865`

| level | nominal_amp | target eps_m | realized mean eps_m | realized/eps_tol |
|---|---|---|---|---|
| e1 | 0.156328 | 0.025 | 0.0271776 | 0.2718 |
| e2 | 0.176074 | 0.0435275 | 0.0438231 | 0.4382 |
| e3 | 0.188725 | 0.0757858 | 0.0718512 | 0.7185 |
| e4 | 0.208391 | 0.131951 | 0.135123 | 1.3512 |
| e5 | 0.230106 | 0.22974 | 0.228416 | 2.2842 |
| e6 | 0.286178 | 0.4 | 0.409721 | 4.0972 |

### HP-D3

- eps_tol = `0.05`
- eps_tol source: src/p2/mrs/d3.py R_mp3 idempotency tol 1e-9 is not an accuracy scale. Surrogate 0.05 (= MP2/MP5 slack) on mean |p_mut - p_ref| vs well-regularized ref.
- window: delta_r=`0`, eta_bar=`1e-06`, halfwidth=`2e-06`

| level | nominal_amp | target eps_m | realized mean eps_m | realized/eps_tol |
|---|---|---|---|---|
| e1 | 0.306846 | 0.0125 | 0.0125019 | 0.2500 |
| e2 | 0.57716 | 0.0217638 | 0.0218068 | 0.4361 |
| e3 | 1.15828 | 0.0378929 | 0.0384077 | 0.7682 |
| e4 | 2.52061 | 0.0659754 | 0.0661658 | 1.3233 |
| e5 | 6.66228 | 0.11487 | 0.115065 | 2.3013 |
| e6 | 25.1487 | 0.2 | 0.199543 | 3.9909 |

## Realized-axis span check

Target span per curve: [0.25, 4.0] × eps_tol (log-spaced, 6 levels).

- CE-A1: realized/tol ∈ [0.251, 3.995] (target [0.25, 4.0])
- CE-B3: realized/tol ∈ [0.252, 4.022] (target [0.25, 4.0])
- CE-C1: realized/tol ∈ [0.250, 4.005] (target [0.25, 4.0])
- CE-D3: realized/tol ∈ [0.249, 4.050] (target [0.25, 4.0])
- HP-A1: realized/tol ∈ [0.287, 3.904] (target [0.25, 4.0])
- HP-B3: realized/tol ∈ [0.265, 4.907] (target [0.25, 4.0])
- HP-C1: realized/tol ∈ [0.272, 4.097] (target [0.25, 4.0])
- HP-D3: realized/tol ∈ [0.250, 3.991] (target [0.25, 4.0])

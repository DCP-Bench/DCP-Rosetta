# Research: Hexaly Optimizer, Python

## Identity

- Product: Hexaly Optimizer 15.0 (formerly LocalSolver), vendor Hexaly.
- Python package: `hexaly` on PyPI, 15.0.20261026 (released 2026-10-27), wheels only
  (Linux glibc 2.28+ x86-64 and ARM64, Windows x86-64, macOS).
- Native API: `hexaly.optimizer` (`HexalyOptimizer`, `HxModel`, `HxExpression`, `HxParam`,
  `HxSolution`, `HxSolutionStatus`, `HxError`).

## Licence

- Every optimizer needs `license.dat`. Lookup: `HX_LICENSE_PATH` (the file), working
  directory, `/opt/hexaly_15_0/license.dat`; `HxVersion.set_license_path/content`.
- The licence used here: academic, 1 concurrent use, 1 machine, no hardware signature,
  Hexaly up to 16.0, expires 2027-01-31. It works offline in a container without network.
  Three containers solving at once were not refused: the concurrency limit is not
  enforced offline, so runs are kept serial by hand.

## Modelling concepts

Decisions: bool, int(lo, hi), float(lo, hi), list(n), set(n), interval(lo, hi),
optional_interval. Expressions: arithmetic, comparisons, logic, iif, at, min/max, abs,
sum/prod, count, contains, distinct, partition, cover, disjoint, sort, index, lambdas
over ranges. No all-different global. At least one objective required.

## Statuses

OPTIMAL (bound reached within gap_limit, default 1e-4), FEASIBLE, INFEASIBLE (nothing
found, unproven), INCONSISTENT (proven infeasible).

## Probes (probes/p01..p17)

| Probe | Finding |
|---|---|
| p01 | licence works offline, unprivileged, read-only root |
| p02, p03 | no objective is an error; minimize(0) works; INCONSISTENT only via presolve; pigeonhole 6/5 unproven |
| p04 | hard no-goods never prove exhaustion |
| p05 | gap_limit 1e-4, nb_threads 0, 64-bit ints, list/array values, error texts |
| p06 | 3 concurrent containers all solved |
| p07, p08 | 3-queens unproven as hard constraints, proven as minimised violations |
| p09 | soft no-goods prove exhaustion (x+y=2, 5 Booleans, perm3, 6-queens, 8-queens) |
| p10 | time_limit is an int; log writer bound at optimizer creation |
| p11, p12, p13 | knapsack, colouring proven; ft06 needs 4 threads (or a disjunctive int model) |
| p14 | `/` float, `//` floor, `%` truncating, `**` float; distinct(array) as all-different |
| p15 | assignment: Booleans and pairwise != proven, distinct and list unproven |
| p16 | default gap reports OPTIMAL with an open bound |
| p17 | infeasibility and enumeration findings hold with 4 threads |

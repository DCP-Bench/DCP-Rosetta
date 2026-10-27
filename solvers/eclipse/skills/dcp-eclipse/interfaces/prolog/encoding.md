# Choosing an encoding (ECLiPSe, Prolog)

Back to [the Prolog interface](README.md).

All numbers measured with ECLiPSe 7.2 #13 (cputime inside the system; wall adds 0.28 s start-up).

| Model | Variant | Time |
|---|---|---|
| 8-queens, all 92 solutions | `ic`, decomposed `#\=` | about 0.3 s wall |
| 10-queens, all solutions | `ic` decomposed / `ic` with `alldifferent` triple | 0.03 s / 0.65 s |
| 12-queens, all solutions | `ic` decomposed / `ic` with `alldifferent` / `gfd` decomposed / `gfd` with `alldifferent` | 0.80 / 16.25 / 0.99 / 1.14 s |
| queens, first solution, `first_fail` | `ic` N=100 / N=200 | 0.01 / 9.2 s |
| | `gfd` N=100 / N=200 | 0.04 / 2.52 s |
| | `ic` with `alldifferent`, N=60 / `gfd` with `alldifferent`, N=100 | over 60 s / 0.00 s |
| queens N=30, `input_order` | `ic` / `gfd` | over 60 s / 55.7 s |
| magic square, first solution, `first_fail` | `ic` N=5: `alldifferent` 0.04 s, decomposed 0.01 s | |
| | `ic` N=6: `alldifferent` 3.96 s, decomposed 1.17 s; N=7 both over 60 s | |
| | `gfd` N=4, 5: 0.00 to 0.02 s; N=6 did not finish | |
| job shop ft06 (6x6, optimum 55), `bb_min`, `smallest`/`indomain_min` | `ic_edge_finder` `disjunctive/2` / `ic_edge_finder3` | 0.01 / 0.01 s |
| | `ic_edge_finder` `cumulative/4` limit 1 | 0.01 s |
| | `ic_cumulative` `cumulative/4` limit 1, pairwise reified `or` | no proof in 120 s |
| random 7x7 job shop (optimum 56), `disjunctive/2` | `smallest`/`indomain_min` 0.92 s; `input_order` 4.36; `first_fail` 0.34; `smallest`/`indomain_max` 4.76; `smallest`/`indomain_split` 0.93; `anti_first_fail` 15.55 | |
| | `restart` 0.94, `dichotomic` 0.93; `ic_edge_finder3` 0.01; `ic_edge_finder` `cumulative/4` 0.38; `ic_cumulative` and pairwise over 60 s | |
| 8x8 job shop (seed 7) | `ic_edge_finder3` `first_fail` 0.05 s; `ic_edge_finder3` `smallest`, `ic_edge_finder` `first_fail` and `cumulative/4` `first_fail` over 60 s | |
| 10x10 job shop | no proof in 60 s; `bb_options{timeout:5}` returned 90 | |

What follows from the numbers:
- **Decomposed `#\=` beat `alldifferent` in `ic` on queens and magic squares** (12-queens 0.80 against 16.25 s). In `gfd` the two were close.
- **`gfd` goes further on first solutions** (queens N=200 in 2.52 s against 9.2 s) and with `alldifferent`.
- **Scheduling: `disjunctive/2` or `cumulative/4` from `ic_edge_finder`**, not `ic_cumulative` and not pairwise `or`.
- **Search order decides heavy-tailed scheduling runs**: `first_fail` was best on 7x7 and on one 8x8, and the same order timed out on another 8x8 with a different propagator. Try two orders and cut with `bb_options{timeout:T}`.
- `strategy:restart` and `dichotomic` did not change the 7x7 time.


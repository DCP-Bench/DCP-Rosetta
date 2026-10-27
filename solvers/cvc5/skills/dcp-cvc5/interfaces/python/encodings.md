# cvc5 in Python: encodings and performance

Part of [the Python interface](README.md). Shared concepts: [SKILL.md](../../SKILL.md).

## Choosing an encoding

Measured on puzzles and designs between 10 and 400 variables, default logic, 180 s limit.

- **Boolean atoms and clauses beat integer sums on combinatorial designs.** Replacing `Int`
  variables, `Distinct` and `Sum(If(...))` counts by one-hot Booleans with exactly-one and
  at-most-one clauses solved what timed out otherwise: a Steiner system on 13 points
  (clauses plus one degree sum, 7 s), a word-design code (12 s), a round-robin schedule
  (10 s), n-queens 14 to 16 (1 s). A permutation with a cost, such as a rehearsal order,
  was fast as pairwise order Booleans plus transitivity clauses (5 s) and timed out as
  `Distinct` over slot variables.
- **Costs and capacities: 0/1 integer variables with linear rows.** A warehouse location
  model went from 157 s with `If` sums to 4.7 s with `x[t][w] <= open[w]` and plain linear
  capacity and cost rows.
- **Products of variables: case-split over a constant.** `Or([And(d == a, p == a * t) for a
  in range(1, 10)])` made a three-factor digit puzzle solve in 3 s after the product form
  timed out. A square test is an `Or` over the constant squares up to the bound.
- **Large products: bit-vectors.** `BitVec`, `ZeroExt` to double width and `BV2Int` solved
  products of four factors near 10^9 that timed out as integers. `<=` on bit-vectors is
  signed: give a constant bound one extra bit, or it reads as negative and the model is
  silently unsat.
- **Write counters and definitions as clauses.** A sequential counter over 200 Booleans
  written as `v == Or(prev, And(lit, prev_j))` made `check()` run for more than 800 s, past
  `tlimit-per`. The same counter as four implication clauses (`v -> prev or lit`,
  `v -> prev or prev_j`, `prev -> v`, `lit and prev_j -> v`) solved in seconds. Use it for
  at-most-k windows and cardinalities; one clause per forbidden subset also worked.
- **A no-good over `BV2Int` terms of bit-vector variables needs `bv-solver=bitblast-internal`.** A model on
  `BitVec` letters with `ULE` bounds and `Distinct` solved a 10-letter cryptarithm in 0.3 s
  with a bit-vector blocking clause, but the default `bv-solver=bitblast` stalled for
  170 s once a no-good over `BV2Int` terms of the letters was added. With `SolverFor("ALL")` and
  `s.set("bv-solver", "bitblast-internal")` it took 13 to 17 s. `solve-int-as-bv` fails on an
  incremental solver (`solveIntAsBV not supported with incremental solving`).
- **Tours and routes: prune arcs before encoding.** With Int arcs, degree rows and an order
  encoding, the optimality proof of a 12-city tour took 74 to 102 s and 20 cities timed out.
  Computing in Python, from the distance matrix only, an assignment lower bound (Hungarian
  method, reduced costs as arc coefficients), a tour upper bound (nearest neighbour plus 2-opt)
  and a 1-tree bound that drops arcs which cannot be on a tour within the upper bound made all
  instances solve in under 3 s, up to 30 cities. Cheapest-in and cheapest-out bounds alone did
  not help.
- **Redundant totals help.** Adding a derived equality (the cells of a magic hexagon sum to
  n(n+1)/2, the line sums of a heterosquare lie between the sum of the smallest and of the
  largest values) made two timeouts solve.
- **Tightening for optimisation is the weak spot.** Every step ends in an unsat proof over
  all the objective terms; weighted sums of 100 conditional terms timed out on a 10x10 grid.
  The second solution of a satisfaction problem is the same kind of proof and can stall when
  the instance is a pigeonhole in disguise.

## Performance

Measured with cvc5 1.4.2, with `tlimit-per` set to 60 s per `check()`.
Times are wall-clock for one run of a script, model building included (building
took under 0.02 s in every case). These are the measurements behind the advice above.

| Model | Config | Result | Time |
|---|---|---|---|
| pigeons 7 into 6 holes (`Distinct`, bounded ints) | `Solver()` | unsat | 0.70 s |
| pigeons 7 into 6 holes | `SolverFor("QF_LIA")` | unsat | 0.57 s |
| pigeons 8 into 7 holes | `Solver()` | unsat | 7.8 s |
| pigeons 8 into 7 holes | `SolverFor("QF_LIA")` | unsat | 5.8 s |
| pigeons 9 into 8 holes | either | unknown, TIMEOUT | 60 s |
| magic square 4x4 | `Solver()` | sat | 0.31 s |
| magic square 4x4 | `QF_LIA` | sat | 0.23 s |
| magic square 4x4 | `QF_LIA`, `arith-prop` none | sat | 0.47 s |
| n-queens 8 | either | sat | under 0.05 s |
| n-queens 20 (`Distinct` on rows and diagonals) | `Solver()` | unknown, TIMEOUT | 60 s |
| n-queens 20 | `QF_LIA` | sat | 1.1 s |
| n-queens 40 | `QF_LIA` | sat | 13.0 s |
| n-queens 40 | `QF_LIA`, `arith-brab` off | sat | 13.0 s |
| n-queens 40 | `QF_LIA`, `arith-prop` none | sat | 32.9 s |
| job shop ft06 (6 jobs x 6 machines), horizon 55 | `Solver()`, `QF_LIA`, `QF_LIA` with `arith-prop` none | sat | 0.07 to 0.15 s |
| job shop ft06, horizon 54 | `Solver()`, `QF_LIA`, `QF_LIA` with `arith-brab` off | unsat | 0.12 to 0.14 s |

Takeaways. Set `QF_LIA` for linear models: the default logic timed out on 20-queens where
`QF_LIA` solved it in 1.1 s. Pairwise no-overlap disjunctions were fast on this job shop;
measure before trying other encodings at larger sizes. Pigeonhole-style models hit the
limit quickly at 9 into 8; add redundant bounds or reformulate.

Nonlinear integer arithmetic (`QF_NIA`, products of two or more variables): cvc5 decided
the small cases tested (`a*b == 143` sat with `a = 13, b = 11`; `a*a == 2` unsat;
`a*b == 7` with bounds unsat). For a product of two primes near 10^6 it returned
`unknown` with reason `TIMEOUT` after 20 s. The solver can return `unknown` on nonlinear
problems, so treat it as incomplete. Do not expect a definite answer on large products.


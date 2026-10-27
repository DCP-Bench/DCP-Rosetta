---
name: dcp-essence-prime
description: Essence' constraint modelling language run with Savile Row and its bundled Minion CP solver (given/find/letting, matrices, globals, minimising/maximising, .param files, solution files, -all-solutions, branching). Use when writing, running or debugging .eprime models, or when the user has chosen Essence', Savile Row or Minion.
license: Apache-2.0
compatibility: Requires Savile Row (tested 1.11.1, Linux tarball with Minion bundled) and Java 15+ on PATH; free, no licence key. Examples that read JSON use Python 3 (standard library only).
metadata:
  domain: constraint-programming
  solver: minion
  paradigm: cp
  interfaces: "essence_prime"
---

# Essence' with Savile Row and Minion

Essence' is a typed CP modelling language. Savile Row reads a model (`.eprime`) plus a parameter file (`.param`), reformulates it, writes Minion input, runs Minion and turns its answer back into Essence' text (`letting NAME be VALUE`). Keep in mind: **everything is finite and ground before search** (every domain and index range comes from constants or parameters), and the model is compiled fresh for each parameter file.

## Pick an interface

Read this file, then the interface file.

| | Essence' text through Savile Row |
|---|---|
| Read | [interfaces/essence_prime.md](interfaces/essence_prime.md) |
| Package | Savile Row (tarball with Minion bundled; Java 15+) |

Other bindings are not covered yet.

Contents: [Modelling rules](#modelling-rules) · [Pitfalls](#pitfalls) · [Search and performance](#search-and-performance) · [Common issues](#common-issues) · [Further reading](#further-reading) · Language reference: [references/essence_prime/language.md](references/essence_prime/language.md) · Install, files, running and enumeration: [interfaces/essence_prime.md](interfaces/essence_prime.md)

Examples (each runs with its README's command): [satisfy](assets/essence_prime/send-more-money/README.md) · [all solutions](assets/essence_prime/queens-all/README.md) · [maximise](assets/essence_prime/knapsack/README.md) · [all optimal](assets/essence_prime/all-optimal/README.md) · [minimise](assets/essence_prime/vertex-cover/README.md) · [infeasible](assets/essence_prime/pigeonhole/README.md) · [scheduling](assets/essence_prime/scheduling/README.md) · [job shop, no-overlap](assets/essence_prime/jobshop/README.md) · [JSON data, ragged lists](assets/essence_prime/json-input/README.md)

## Modelling rules

- Items listed together in a clue (`X, the chef, and the police officer`) are distinct unless the statement says otherwise.
- Prefer globals: `allDiff`, `gcc`, `atleast`, `atmost`, `table`, `cumulative`, `alldifferent_except`. Use quantifiers over decompositions by hand.
- Tight domains from the data (`int(0..sum(values))`). Add `where` on parameters only to validate input.
- Put matrices of the same shape in one `find`, not many scalars.
- Every size that varies between data sets must be a `given` (or a `letting` computed from givens); a matrix declared with one data set's numbers fails on the next with `Index domains do not match for the matrix F`.
- Ragged data (lists of different lengths) has no direct form: pad rows to the longest with a value outside the real range and pass a row-length matrix; read row `i` only up to `len[i]`, since padding can equal a real value ([example](assets/essence_prime/json-input/README.md)). No strings or floats: map names to integers before writing the param file.
- No-overlap on a machine (one task at a time): post each pair of tasks as an either-or, `(a < b /\ mach[a] = mach[b]) -> ((s[a] + d[a] <= s[b]) \/ (s[b] + d[b] <= s[a]))` over a flat task list; a precedence within a job is an implication on its job index. Solved job shop with 9 tasks to proven optimum ([example](assets/essence_prime/jobshop/README.md)). For a resource with a shared capacity, use `cumulative` instead.
- Symmetric designs (round-robin, periodic schedules): fix the first period to canonical values. A set of rows: `M[r,..] <=lex M[r+1,..]` orders them.
- No square root: the nearest integer to sqrt(s) is `letting R = sum([d | d : int(0..DMAX), (2*d-1)**2 <= 4*s, 4*s < (2*d+1)**2])` (verified for s = 0, 2, 10, 13, 24). `^` does not parse; use `**`.

## Pitfalls

- A quantifier body extends as far right as possible: `sum i : D . a[i] <= c` is a sum of booleans and fails with `'And' contains something other than a relation`. Write `(sum i : D . a[i]) <= c`. Likewise `forAll i : D . A /\ B` puts both under the quantifier.
- `abs(x)` does not parse; write `|x|`. No if-then-else, no `element`, no `negativeTable`: use `(c -> A) /\ (!c -> B)`, an index `M[idx]` with a decision variable, or `table` with a complement built by a comprehension.
- Division floors and `%` follows it (`(-3)/2 = -2`, `(-3)%2 = 1`). `**` is right associative.
- An out-of-range index or division by zero makes the enclosing constraint false, not an error.
- Bool converts to int in arithmetic, int does not convert to bool.
- Global arguments must be one-dimensional: slice (`M[i,..]`) or `flatten`. `atleast/atmost(X, Counts, Vals)` but `gcc(X, Vals, Counts)`.
- `sum(M)` and `max(M)` need a 1-D matrix: write `sum(flatten(M))` for 2-D. `forAll i : D1, j : D2` with different domains does not parse: nest the quantifiers.
- Parameter-only positions (set `in`, `table` tuples, quantifier and sum bounds, `where`) take no decision variables.
- Reserved words cannot be names (`find max` fails with `Parsed keyword 'max'`, `find where` with `Parsed 'find' keyword.`); rename, e.g. `max_`. List: [references/essence_prime/language.md](references/essence_prime/language.md#declarations).
- A sequence generated by a recurrence and cut at a bound needs its index domain wider than the bound, or the model is unsatisfiable.
- A quantifier over a large domain (primality over 1..10000) exhausts Savile Row's memory (a 1.2 GB heap in one measured setup; the launcher's default is 8 GB). Precompute the set as a `letting` list and quantify over that.
- Savile Row compiles slowly for large grids and reads the whole model before search, so a large instance can time out before Minion starts (`SavileRowTimeOut:1`); keep matrix dimensions small and quantifier bounds fixed.

## Search and performance

- `branching on [x, M, [M[i,i] | i : int(1..n)]]` fixes variable order (flatten order for matrices). A comprehension is one entry of the list, so wrap it: `[[e | i : D]]`. Branch first on the structural decisions the rest follows from, then the rest. Branch on few-valued variables that fix the objective.
- `heuristic static|sdf|conflict|srf` (Minion only) goes before `such that` and before the objective. Try `sdf` (smallest domain first) when the default stalls, and `conflict` too: it solved one scheduling model where `sdf` and `srf` did not. On others neither helped; value-symmetry breaking did.
- Restrict decisions to a precomputed admissible set: `letting S = [i | i : int(1..N), cond]` and `x in toSet(S)`. Grid paths: branch on a Boolean cell matrix, not on position arrays. Long sequences: try a position model (variable = value at each position) early.
- Boolean incidence matrices (`x[i,s]` bool) propagate much better than weighted sums such as `sum i : D . toInt(x[i] = s) * i`. Products of decision variables in an objective prove poorly; keep the objective linear where you can.
- Symmetric models (partitions, interchangeable items, large symmetric Boolean matrices): order the entries within each set, and add implied totals (sums, sum of squares halved).
- Implied constraints on sums, tighter domains and a sorted symmetric copy help more than extra branching. Scheduling optimisations: a `cumulative` per resource, with the implied bounds, proved what `sdf` and bounds alone did not ([example](assets/essence_prime/scheduling/README.md)).
- An optimum that is not proven within the limit comes back with `SolverTimeOut:1`: tighten the objective's domain and add implied bounds rather than only raising the limit.

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| `'And' contains something other than a relation` | quantified `sum` compared without parentheses | [Pitfalls](#pitfalls): `(sum i : D . e) <= c` |
| `Parsed entry in list` on `branching on` | bare comprehension in the list | `branching on [[e \| i : D]]` |
| `Expected one-dimensional matrix in sum function` | `sum(M)` on 2-D | `sum(flatten(M))` |
| `Parsed keyword 'max'` / `Parsed 'find' keyword.` | reserved word as a name | rename (`max_`) |
| parse error at `branching on` / `heuristic` | placed after the objective | move before `minimising` |
| Java `OutOfMemoryError` | large quantifier domain or heap too small | precompute sets; adjust `-Xmx` |

More symptoms (running, files, enumeration, limits): [interface Common issues](interfaces/essence_prime.md#common-issues).

## Further reading

- Savile Row manual: `savilerow-manual.pdf` in the tarball, or [arXiv:2201.03472](https://arxiv.org/abs/2201.03472) (2.1 expressions, 2.2 declarations, 2.4 objective, 2.5 branching, 4.3-4.5 files and options).
- Language definition: [Essence' description, arXiv:1601.02865](https://arxiv.org/abs/1601.02865).
- Releases: <https://www-users.york.ac.uk/peter.nightingale/savilerow/releases.html>; example models ship in the tarball's `examples/`.

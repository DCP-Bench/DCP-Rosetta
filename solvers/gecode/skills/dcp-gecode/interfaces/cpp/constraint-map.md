# Constraint map: read the description, pick the global

Part of [Gecode in C++](README.md); shared concepts in [SKILL.md](../../SKILL.md).

Write the model clause by clause: for each sentence of the description find its row,
and start each block with a `//` comment in the description's words. Every call takes
the space first (`*this` in the constructor). Arrays are `IntVarArgs`/`IntVarArray`,
constants `IntArgs({..})`. Bracketed semantics are verified in [catalogue.cpp](../../references/cpp/catalogue.cpp);
signatures in [constraints.md](../../references/cpp/constraints.md); reference: [integer constraints](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelInt.html).

| The description says | Post |
|---|---|
| all different | [`distinct(*this, x, IPL_DOM)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntDistinct.html) |
| all different after shifts (queens diagonals) | `distinct(*this, IntArgs(offsets), x)` [x_i + n_i distinct] |
| all different except value c (0 = empty) | `distinct(*this, x, c)` |
| different where selected | `distinct(*this, bools, x)` [only x_i with b_i = 1] |
| exactly / at least / at most k equal to v | [`count(*this, x, v, IRT_EQ / IRT_GQ / IRT_LQ, k)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntCount.html); v or k may be an `IntVar`; v may be an `IntSet` |
| value v_j occurs c_j times (gcc) | `count(*this, x, cards, IntArgs(vals))`, cards `IntVarArgs`; bounds instead: `IntSetArgs` |
| number of distinct values | [`nvalues(*this, x, IRT_EQ, k)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntNValues.html) |
| the number of distinct values is to be minimised (colours, groups used) | `IntVar k(*this, 1, n)`, `nvalues(*this, x, IRT_EQ, k, IPL_DOM)`, then BAB on `k` with `precede` on the values; [recipe](../../references/cpp/modelling.md#recipes) |
| every window of q has l..u items in S | [`sequence(*this, x, IntSet(S), q, l, u)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntSequence.html) |
| two of them share a group at most once (pairs meet) | per pair: `BoolVarArgs m; m << expr(*this, g[p][r] == g[q][r])` over rounds r, then `linear(*this, m, IRT_LQ, 1)` |
| how many are true / weighted count | [`linear(*this, bools, IRT_EQ, k)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntLI.html), `linear(*this, IntArgs(w), x, IRT_LQ, cap)` [Σ w_i·x_i ≤ cap; w = 5m is `IntArgs({1, -5})` over `{w, m}`] |
| the i-th value of a table / array | [`element(*this, IntArgs(table), i, y)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntElement.html) [table[i] = y], `element(*this, xs, i, y)` for variables |
| a cell of a matrix indexed by variables | `element(*this, IntArgs(a), col, w, row, h, z)` [a[col + w*row] = z] |
| allowed combinations / compatibility table | [`TupleSet t(arity); t.add(IntArgs(..))...; t.finalize(); extensional(*this, x, t)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntExt.html); forbidden: `extensional(*this, x, t, false)` |
| a pattern along a sequence (nonogram row, shift rules) | `extensional(*this, x, DFA(reg))`, [`REG`](https://www.gecode.org/doc/6.2.0/reference/classGecode_1_1REG.html) built from `*r` (0+), `+r` (1+), `r(n, m)` (n..m times), `a + b` (concat), `a \| b` |
| visit every node once and return (tour) | [`circuit(*this, succ)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntGraph.html) [succ[i] = next node], with offset `circuit(*this, 1, succ)` |
| tour cost | `circuit(*this, IntArgs(cost), succ, total)` [cost row-major n×n; total = Σ cost[i][succ_i]] |
| Hamiltonian path from s to e | `path(*this, succ, s, e)` [succ has n vars, domain 0..n; succ[e] = n] |
| one task at a time on a machine | [`unary(*this, start, IntArgs(dur))`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntScheduling.html); optional tasks: add `bools` |
| tasks of a job run in order (job shop) | `rel(*this, s_a + d_a <= s_b)` for each consecutive pair, plus one `unary` per machine; [job shop](../../assets/cpp/jobshop-ft06/README.md) |
| resource capacity over time | `cumulative(*this, cap, start, IntArgs(dur), IntArgs(use))`; optional tasks: add `bools`; machine choice: `cumulatives` |
| items into bins with capacities | [`binpacking(*this, load, bin, IntArgs(size))`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntBinPacking.html) [load_j = Σ size_i over bin_i = j]; bound `load` by the capacity |
| rectangles do not overlap | [`nooverlap(*this, x, IntArgs(w), y, IntArgs(h))`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntGeoPacking.html) |
| a sorted copy / order statistics | [`sorted(*this, x, y)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntSorted.html) |
| a permutation and its inverse (position ↔ item) | [`channel(*this, x, y)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntChannel.html) [x_i = j ⇔ y_j = i, both 0-based]; 1-based: `channel(*this, x, 1, y, 1)`; one-hot: `channel(*this, bools, v, offset)` |
| interchangeable values (colours, groups, labels) | [`precede(*this, x, IntArgs({0,1,..,k}))`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntPrecede.html) [value v+1 appears only after v]; LDSB: [search.md](../../references/cpp/search.md#symmetry) |
| interchangeable rows or columns | `rel(*this, rowA, IRT_LQ, rowB)` (lexicographic) |
| an unordered collection (faces of a die, a multiset, a group's members) | `rel(*this, block, IRT_LQ)` (sorted), when nothing fixes the order |
| increasing sequence | `rel(*this, x, IRT_LE)` |
| y is one of x | `member(*this, x, y)` |
| minimum / maximum / position of the maximum | [`min(*this, x, y)`, `max(*this, x, y)`, `argmax(*this, x, i)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelIntArith.html) [first index on ties] |
| a set (team, group, subset) | [`SetVar s(*this, IntSet::empty, lo, hi, cmin, cmax)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelSet.html), `cardinality`, `rel(*this, s1, SRT_DISJ, s2)`, `channel(*this, bools, s)`; read results through the bools |
| x differs from / equals y plus a constant | `rel(*this, x != y + c)`, `rel(*this, x == y + c)` (no `rel(x, IRT_NQ, y, c)` form) |
| arithmetic | [`rel(*this, x * y == z)`, `abs`, `/`, `%`, `sqr`, `pow(e, n)`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelMiniModelArith.html), `divmod(*this, x, d, q, r)` |
| logic between conditions | [`rel(*this, (x == 1) >> (y != 1))`, `&&`, `\|\|`, `!`, `^`](https://www.gecode.org/doc/6.2.0/reference/group__TaskModelMiniModelBool.html); `clause(*this, BOT_OR, pos, neg, 1)` |
| if-then-else value | `ite(*this, b, x, y, z)` or `rel(*this, z == ite(b_expr, x, y))` |

A decomposition is right only when no row fits. Two globals on the same variables are
fine (a `distinct` beside a `linear`); redundant globals often pay (`count` cards that
sum to n, a `cumulative` beside `nooverlap` on each axis). Pass `IPL_DOM` to `distinct`
on permutations and puzzles; keep the default on arithmetic ([propagation levels](../../references/cpp/modelling.md#propagation-levels)).
A variable may appear more than once in a `linear` list: each occurrence adds its coefficient.
`linear(*this, IntArgs({1, 1, 1}), xs, IRT_EQ, 4)` with `xs = {x, x, y}` posts 2x + y = 4
(checked with Gecode 6.2.0); sum the coefficients yourself when that reads better.

Branch on every decision variable ([search.md](../../references/cpp/search.md)).

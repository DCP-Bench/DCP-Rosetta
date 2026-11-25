# groundfox_fox: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how FOX
(first-order model expansion, grounded by GroundFOX and solved by CaDiCaL 3.0.0) expresses it.
Runner: [run.py](run.py), which does everything through [dcp_fox.py](dcp_fox.py): it calls
the submission's `structure(instance)`, writes the FOX `structure` block, grounds the
whole with `groundfox` into DIMACS CNF, solves it with CaDiCaL 3.0.0 (python-sat) and reads
the declared outputs back from the out-predicates of the same name.

**Satisfaction problems only.** FOX has no arithmetic, no aggregates and no objective:
an optimisation problem cannot be expressed.

## Submission file

One Python file, `model.py`, defining:

- `FOX`: a string with the `invocabulary`, `outvocabulary` and `theory` blocks, in the
  default (certified) fragment: every sentence in grounding normal form (GNF), quantifier
  guards over input symbols only, no function symbols. **No `structure` block**: the runner
  writes it.
- `structure(instance)`: a function returning the interpretation of every input symbol.
- optionally `FLAGS`: a list of groundfox options from `--nested-guards`, `--functions`,
  `--arbitrary-fol`, passed to groundfox when the theory needs them (they leave the
  certified fragment; avoid them).

The file may import the standard library only (`json`, `itertools`, `math`). It must not
search: `structure` computes data relations (orderings, sums of data, allowed tuples), never
an answer.

## Entrypoint

The runner imports `model.py` (with stdout redirected to stderr), reads `FOX`, calls
`structure(request["instance"])` once, and appends the generated structure to `FOX`.

## Instance

The instance arrives in `structure(instance)` as the parsed JSON object (`int`, `bool`,
`str`, nested lists), exactly as the brief lists it, 0-based like the JSON. The function
returns a `dict`:

| Key | Value | Written as |
| --- | --- | --- |
| `"domain"` (optional) | iterable of elements | `domain = { ... }`, plus every element used below |
| proposition `P/0` | `True` / `False` | `P = true` |
| unary `Row/1` | iterable of elements | `Row = { 0 ; 1 ; 2 }` |
| `Edge/2`, `Clue/3`, ... | iterable of tuples (or lists) | `Edge = { (0,1) ; (1,2) }` |

- **Elements** are integers or identifiers (`[A-Za-z][A-Za-z0-9_'"-]*`). FOX numbers have
  no sign, so a negative integer `-k` is written as the identifier element `negk` (`-1` is
  `neg1`); write it the same way where the theory names it as a constant. A Boolean or any
  other string is an error naming the symbol: map strings to their index.
- Every symbol of the `invocabulary` must be a key (an empty list is fine); a key that is
  not declared is an error. Arity is checked tuple by tuple.
- **The domain** is the `"domain"` entry plus every element of every interpretation. Every
  value an output can take must be in it: list the output values in a unary input symbol
  (`Val = range(1, n + 1)`) and guard with it.
- FOX has no arithmetic: anything numeric the theory needs (order `Less/2`, successor
  `Next/2`, `Sum3/3`, which pairs attack, which cells a clue covers) is computed here as a
  relation over the data. Only data: no decision depends on it.

## Outputs

Each declared output is an out-predicate with **the output's exact name**, and **the value
is its last argument**, after the 0-based indices:

| Brief | Out-predicate | Atoms true in a solution |
| --- | --- | --- |
| `x: int` | `x/1` | exactly one `x(v)` |
| `queens: [n]int` | `queens/2` | exactly one `queens(i, v)` per `i` in `0..n-1` |
| `grid: [n][m]int` | `grid/3` | exactly one `grid(i, j, v)` per cell |
| `used: [n]bool` | `used/2` | exactly one `used(i, b)`, `b` in `{0, 1}` (a Boolean is given as 0/1) |

- Indices and values must be integer elements; values beyond 32 bits (a 10-digit integer) work, as elements are written as text.
  A value element `negk` reads back as `-k`: an output that can be negative (a `-1`/`+1`
  matrix) takes its values from a data symbol such as `Val = [-1, 1]`. The runner reads the atoms true in the SAT
  model; indices must cover `0..len-1` at each level. Two true values at one index is an
  error ("has two true values"); no true atom at all is an error.
- **Wide integers as digits**: an integer output `x` may instead be declared as
  `x_digits/(k+2)` with atoms `x_digits(i..., p, d)`: exactly one digit `d` in `0..9` per
  position `p` (0 = units) and index tuple; the runner reads `x = Σ d·10^p`. Use it when the
  value is too large to be a domain element of its own (a sum near millions); compute the
  digits with carry chains over a digit addition table.
- **State exactly-one yourself** for every index: "at least one" (`? v [Val(v)] : x(i, v)`)
  and "at most one" (`~x(i, v1) | ~x(i, v2)` for `v1 ~= v2`). Missing at-most-one gives the
  error above; missing at-least-one gives a gap in the indices.
- An atom that no sentence mentions is not in the grounding and reads as false, so out
  atoms outside the guards (an index beyond `n`) never appear.
- Other out-predicates are auxiliary and never reported.

## Objective

None. FOX has no objective; every model is a satisfaction model.

## Solving

- groundfox runs with `-i model.fox -o model.cnf -p model.cfx -t model_symbols.txt` plus
  `FLAGS`. A groundfox error (a parse error, a sentence not in GNF, a guard over an output
  symbol) is `error` with its message.
- **Every grounding is certified**: checkfox then checks the CertiFOX proof log against the
  `.fox` input and the CNF, before any solving. A rejected (or unreadable) proof is `error`
  ("checkfox rejected the GroundFOX proof ..."); running out of time while checking is
  `timeout`. The final status record carries `proof` (`valid`), `cnf_clauses`,
  `ground_seconds` and `proof_seconds`. Proof checking counts against the execution budget.
- The CNF and the proof log are written to the 512 MiB `/tmp`; a grounding too large for it
  (roughly 10^7 clauses) is `timeout` ("the grounding filled /tmp ..."), a resource limit, not
  `error`. Keep groundings well below that.
- CaDiCaL 3.0.0 (`cadical300`, python-sat 1.9.dev25) solves the CNF with default settings, incrementally, in a child process that the runner kills at the deadline.
- **Enumeration**: after each solution the runner adds a clause blocking the current values
  of all output atoms, so a next solution differs in a declared output; auxiliary
  predicates never cause repeats. It stops at `solution_limit` (`limit`); unsatisfiable is
  exhaustion (`complete`, or `unsat` before any solution).
- **Time**: the deadline is `execution_timeout` from the start of solving. groundfox gets the
  time left as a subprocess timeout; each SAT call is interrupted at the deadline
  (`timeout`). A `SIGALRM` at `execution_timeout + 5` s also gives `timeout`.
- Any other exception (a missing `FOX` or `structure`, a bad element, an output that is not
  an out-predicate) is `error` with its message.

## Compilation

None. `structure`, grounding and solving all run inside the execution budget.

## Environment

Image `dcp-eval/groundfox_fox:v1` (`python:3.12.11-slim-trixie`): Python 3.12.11,
`groundfox` and `checkfox` 0.1.2 (commit f30fb9c of
<https://gitlab.kuleuven.be/krr/software/groundfox-checkfox>) in `/usr/local/bin`,
python-sat 1.9.dev25. No network, read-only root, `/tmp` writable, user 65534, 1 CPU and
2048 MiB, as for every integration.

## Traps

- **Two forms ground but fail the proof check** (GroundFOX 0.1.2 writes a proof that
  checkfox rejects with "Proof incomplete: N formula(s) remain", so the run is `error`):
  a sentence without any quantifier (`x(0).`, `~x(0) | y(1).`): wrap it,
  `! u [u = 0] : x(0).`, with a constant of the sentence; and an existential as one
  disjunct beside other literals (`~x(c) | ? k [G(c, k)] : r(k)`): put the literals inside
  its body, `? k [G(c, k)] : r(k) | ~x(c)` (equivalent only when every `G(c, _)` is
  nonempty), or use the universal form `! k [G(c, k)] : ~x(c) | r(k)` when one witness
  suffices; and nested existentials (`? a [D(a)] : ? b [D(b)] : g(a, b)`): introduce an
  auxiliary out-predicate, `? a [D(a)] : h(a).` and `! a [D(a)] : ? b [D(b)] : g(a, b) | ~h(a).`
  In short: an existential passes when it is a whole clause over one literal, or holds the
  rest of the clause in its body.
- **Guards may only use input symbols.** `! r [Row(r) & queens(r, 1)] : ...` is rejected:
  move the output literal into the body as `~queens(r, 1) | ...`.
- **Sentences are clauses with quantifiers (GNF)**: below the `!` quantifiers, a
  disjunction of literals and `?` quantifiers; `&` only between `!`-quantified
  conjuncts. `=>`, `<=>` and `~( ... )` around anything but an atom are rejected: write
  `a => b` as `~a | b`, and an equivalence as two sentences.
- **Equality is between terms**: `~(x = y)` or `x ~= y` in a guard; `=` cannot compare an
  output.
- **Ground size**: every `!` multiplies the clause count by the guard's size. Keep guards
  tight (precompute a relation of the allowed tuples instead of quantifying over the
  whole domain).
- **Take every quantity from the instance**: a model that hardcodes the example passes it
  and is rejected on the next instance.

## Standalone run

`dcp_fox.py` is also the reader's driver: with `groundfox` on `PATH` and
`pip install python-sat`, `python dcp_fox.py model.py instance.json` grounds the model on
the instance (one object, or the first of a list) and prints one solution as JSON
(`--solutions N` for more). A model opens with a header comment:

```
# <problem>: a FOX model for GroundFOX from DCP Rosetta.
#
# <the problem statement>
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json
```

## Example

The pilot fixture [tests/fixtures/model_groundfox.py](../../../tests/fixtures/model_groundfox.py)
(instance fields `n`, `optimize`; outputs `x`, `y`; satisfaction instance only):

```python
FOX = """
invocabulary { Val/1 Sum/2 }
outvocabulary { x/1 y/1 }
theory {
    ? a [Val(a)] : x(a).
    ! a [Val(a)] : ! b [Val(b) & ~(a = b)] : ~x(a) | ~x(b).
    ? a [Val(a)] : y(a).
    ! a [Val(a)] : ! b [Val(b) & ~(a = b)] : ~y(a) | ~y(b).
    ! a : ! b [Val(a) & Val(b) & ~Sum(a, b)] : ~x(a) | ~y(b).
}
"""

def structure(instance):
    n = instance["n"]
    return {"Val": range(n + 1),
            "Sum": [(a, b) for a in range(n + 1) for b in range(n + 1) if a + b == n]}
```

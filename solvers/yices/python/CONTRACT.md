# yices_python: how this integration realises the submission contract

Read [the submission contract](../../CONTRACT.md) first; this file only says how Yices
(Python bindings) expresses it. Runner: [run.py](run.py), which imports `flatten` and
`mapped` from [runner/runtime.py](../../../runner/runtime.py) and has its own protocol
output, solve and enumeration loop.

## Submission file

One Python file, `model.py`. It may import `yices` (the `Terms`, `Types`, `Config`, ...
classes of the Python bindings) and the standard library. No other file of yours is
staged. The module must not create a `Context`, check or solve anything: it only builds
terms.

## Entrypoint

```python
def build(instance) -> tuple[list[int], dict] | tuple[list[int], dict, tuple[str, int]]
LOGIC = "QF_NIA"   # optional module-level string
```

The runner imports the file and calls `build(instance)` once. It must return a 2-tuple
`(formulas, outputs)` for a satisfaction problem, or a 3-tuple
`(formulas, outputs, (direction, objective))` for an optimisation problem, where
direction is `"minimize"` or `"maximize"`. `formulas` is a list or tuple of Boolean Yices
terms (a single Boolean term is also accepted). Yices terms are plain Python `int`
handles. The optional module-level `LOGIC` selects the logic of the contexts the runner
creates (see [Solving](#solving)). Anything the module prints goes to stderr.

## Instance

`instance` is the JSON object as a plain Python `dict`: integers, Booleans, strings, and
nested `list`s, 0-based. Build every constant from it with `Terms.integer(value)`.

## Outputs

`outputs` is a non-empty `dict` mapping each declared output name to an integer or Boolean
Yices term, a Python `bool`, or a nested list/tuple of these with the declared shape.
After a model is found, each term is read with `Model.get_value` (a model taken with
`keep_subst=1`): a Boolean term comes back as `True`/`False`, an integer term as a Python
`int`. A Python `bool` leaf passes through as a constant. A Python `int` leaf is a term
handle, never a constant: build a constant with `Terms.integer(v)`.

Leaf checks, before solving, give `execution_error` naming the problem: a leaf that is not
an int handle, or a term that is neither Boolean nor integer (a real, a bit-vector). Values
must fit in 64 bits (`2**40` is fine); a larger value reads back as a float and is an
`execution_error`. `Terms.integer` itself silently wraps beyond 64 bits (use
`Terms.parse_rational` for such constants; the runner cannot report them). An output
term that no formula mentions is read as 0 or `False` and enumerated like any other, over
its whole unbounded domain.

## Objective

The third element of the return value: `("minimize", term)` or `("maximize", term)`, with
`term` an integer Yices term. A Python `bool` or `float`, or a term that is not integer, is an
`execution_error`; a Python `int` is read as a term handle, never as a constant, and is rejected only when that
handle is not an integer term, so always pass a term built from the model's variables. Only the third element declares the objective. Solutions are only
reported at the proven optimum.

## Solving

- Contexts: the runner owns every context; terms are global, so it rebuilds contexts from
  the returned `formulas` whenever it needs one. With no `LOGIC` it uses `Context()` (the
  default configuration, which accepts assertions after a satisfiable check). With
  `LOGIC = "QF_NIA"` (or another logic name) it builds
  `Config().default_config_for_logic(LOGIC)`; `QF_NIA` selects MCSAT, which is the only way
  to solve products of unknowns. An unknown logic is `execution_error`
  (`unknown logic`). Nothing else is configured (no parameters, no random seed).
- Time: `execution_timeout` is measured from the start of `solve`, including `build`. Each
  `check_context` gets **all the time left** (`check_context(timeout=left)`, a timer that
  calls `stop_search`); the budget is not split between tightening steps. `INTERRUPTED`
  gives `timeout`. `UNKNOWN` gives `timeout` when the deadline has passed, otherwise
  `error` (`yices returned unknown`). A `SIGALRM` at `execution_timeout + 5` s becomes
  `timeout` as a backstop that only fires between Python bytecodes.
- Optimisation (Yices has no optimiser): one context holds the formulas. Each `SAT` result
  records the objective value `best` and permanently asserts `objective < best` (minimise)
  or `objective > best` (maximise). `UNSAT` after at least one `SAT` proves `best`
  optimal. `UNSAT` at the first check is `unsat`. `INTERRUPTED` or running out
  of time before the proof is `timeout`; `UNKNOWN` follows the Time rule (`timeout` past the deadline, otherwise
  `error` `yices returned unknown`). In every case no solution is emitted.
- Enumeration after the proof: a **fresh** context over the formulas plus
  `objective == best`. Each model is emitted, then a no-good (the disjunction of
  `leaf != value` over every distinct non-constant output leaf, with a Boolean leaf
  negated or not) is asserted and the context is checked again. `UNSAT` gives `complete`
  after at least one solution (`unsat` if there was none); `limit` once `solution_limit`
  is reached. A repeated assignment of the leaves is skipped, not counted.
- Satisfaction: the same enumeration loop, without the objective.
- Exceptions raised while building or solving map to `error` (reported as
  `execution_error`) with the message as the detail: bare for `ValueError` and `YicesException`, `Type: message`
  otherwise. The exception is `TimeoutError`, reported as `timeout` whatever raised it, including the
  submission's own code. A `YicesException` carries Yices's
  own text, for example `The function yices_assert_formulas failed because: the context
  does not support non-linear arithmetic` for a product of two unknowns in the default
  context.

## Compilation

None.

## Environment

Image `dcp-eval/yices_python:v1`, built `FROM python:3.12.11-slim-bookworm` (pinned by
digest). Yices 2.7.0 built from source with MCSAT (libpoly 0.2.1, CUDD 3.0.0) under
`/opt/yices`, registered with `ldconfig`; Python 3.12.11 at `/usr/local/bin/python`; the
`yices` bindings 1.1.6 from PyPI. Nothing else besides pip: the shared
`runner/requirements.txt` stack is not installed, so NumPy is not available. The JSON
library is the standard library's `json`. No edition or size limits (Yices is GPL-3.0).

Inside the container: no network, a read-only filesystem except `/tmp`, user 65534, the
submission and `request.json` under `/input`. The image's entrypoint is the runner
(`python /opt/runner/run.py`). The runner points file descriptor 1 at stderr, so a
`print` or a C-level print from libyices cannot corrupt the protocol.

## Traps

- No operator overloading: `x > 3` is a Python `bool` and `x + 1` is a Python `int`
  (some other handle), not a term. A Python `bool` among the formulas is an
  `execution_error` (`... is a Python bool, not a Boolean Yices term`). Use
  `Terms.arith_gt_atom`, `Terms.add`, and so on.
- Decision variables are `Terms.new_uninterpreted_term(Types.int_type(), name)`. A
  `Terms.new_variable` term is a bound variable and fails at assertion
  (`assertion contains a free variable`).
- Integers are unbounded: add the bounds the problem implies for every output and
  auxiliary term, or enumeration does not stop usefully at `solution_limit`.
- Nonlinear products need `LOGIC = "QF_NIA"`; without it the run is an `execution_error`
  with the message above. Other logics restrict what can be asserted (`QF_BV` rejects
  arithmetic, for instance).
- Do not use `Context.assert_blocking_clause` to enumerate: it blocks the Boolean atom
  assignment, not the integer values, and stops early. The runner's own no-goods cover the
  declared outputs only.
- Bit-vector, real and other sorts are not accepted as output or objective terms.
- Optimisation is linear solution-improving search: a wide objective range can make the
  proof slow, and the result is then `timeout`.
- Quantifiers are untested, and push/pop in the submission has no effect: the runner never sees the
  submission's context.

## Example

The pilot fixture [tests/fixtures/model_yices.py](../../../tests/fixtures/model_yices.py)
(instance fields `n`, `optimize`; outputs `x`, `y`):

```python
from yices import Terms, Types


def build(instance):
    n = instance["n"]
    x = Terms.new_uninterpreted_term(Types.int_type(), "x")
    y = Terms.new_uninterpreted_term(Types.int_type(), "y")
    total = Terms.add(x, y)
    # Yices integers are unbounded, so the bounds the reference declares must be added.
    bounds = [Terms.arith_geq_atom(v, Terms.integer(0)) for v in (x, y)]
    bounds += [Terms.arith_leq_atom(v, Terms.integer(n)) for v in (x, y)]
    if instance["optimize"]:
        return bounds + [Terms.arith_geq_atom(total, Terms.integer(n))], {"x": x, "y": y}, ("minimize", total)
    return bounds + [Terms.arith_eq_atom(total, Terms.integer(n))], {"x": x, "y": y}
```

"""N-queens with Yices: one placement, or unsatisfiable.

Row i gets a column q_i in 0..n-1. Columns are distinct, and no two queens
share a diagonal: for rows i < j, q_i - q_j differs from i - j and from j - i.
"""
import json
import sys
from pathlib import Path

from yices import Context, Model, Status, Terms, Types

n = json.loads(Path(sys.argv[1]).read_text())["n"]

INT = Types.int_type()
zero = Terms.integer(0)
q = [Terms.new_uninterpreted_term(INT, f"q_{i}") for i in range(n)]

ctx = Context()

# Each queen is on the board.
for c in q:
    ctx.assert_formula(Terms.arith_geq_atom(c, zero))
    ctx.assert_formula(Terms.arith_leq_atom(c, Terms.integer(n - 1)))

# No two queens share a column.
if n > 1:
    ctx.assert_formula(Terms.distinct(q))

# No two queens share a diagonal.
for i in range(n):
    for j in range(i + 1, n):
        diff = Terms.sub(q[i], q[j])
        ctx.assert_formula(Terms.arith_neq_atom(diff, Terms.integer(i - j)))
        ctx.assert_formula(Terms.arith_neq_atom(diff, Terms.integer(j - i)))

if ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    queens = [model.get_value(c) for c in q]
    model.dispose()
    print(json.dumps({"queens": queens}))
else:
    print(json.dumps({"status": "unsatisfiable"}))
ctx.dispose()

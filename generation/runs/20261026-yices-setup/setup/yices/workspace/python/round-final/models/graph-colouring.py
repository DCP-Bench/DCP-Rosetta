"""Graph colouring with Yices, minimising the number of colours used.

Each node gets an integer colour in 0..n-1; adjacent nodes differ. The number
of colours used is the sum over colours k of 1 when some node has colour k.
The bound is tightened after each model until the solver proves optimality.
"""
import json
import sys
from pathlib import Path

from yices import Context, Model, Status, Terms, Types

inst = json.loads(Path(sys.argv[1]).read_text())
n = inst["n_nodes"]
edges = inst["edges"]

if n == 0:
    print(json.dumps({"colour": []}))
    sys.exit(0)

INT = Types.int_type()
zero = Terms.integer(0)
one = Terms.integer(1)
col = [Terms.new_uninterpreted_term(INT, f"c_{i}") for i in range(n)]

ctx = Context()

# Colours are in 0..n-1.
for c in col:
    ctx.assert_formula(Terms.arith_geq_atom(c, zero))
    ctx.assert_formula(Terms.arith_leq_atom(c, Terms.integer(n - 1)))

# The two endpoints of every edge get different colours.
for i, j in edges:
    ctx.assert_formula(Terms.arith_neq_atom(col[i], col[j]))

# Objective: the number of colours that some node uses.
used = [Terms.ite(Terms.yor([Terms.arith_eq_atom(c, Terms.integer(k)) for c in col]), one, zero)
        for k in range(n)]
objective = Terms.sum(used)

best = None
best_col = None
while ctx.check_context() == Status.SAT:
    model = Model.from_context(ctx, 1)
    cols = [model.get_value(c) for c in col]
    model.dispose()
    best_col = cols
    best = len(set(cols))
    # Ask for a colouring with strictly fewer colours.
    ctx.assert_formula(Terms.arith_lt_atom(objective, Terms.integer(best)))
ctx.dispose()

if best_col is None:
    print(json.dumps({"status": "unsatisfiable"}))
else:
    print(json.dumps({"colour": best_col}))

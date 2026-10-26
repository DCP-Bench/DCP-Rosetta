# n-queens, all solutions: queen i sits in row i, q[i] is its column.
from yices import Context, Model, Status, Terms, Types

n = 5
INT = Types.int_type()
num = Terms.integer
q = [Terms.new_uninterpreted_term(INT, f"q{i}") for i in range(n)]

ctx = Context()
# every queen is on the board
for t in q:
    ctx.assert_formulas([Terms.arith_geq_atom(t, num(0)), Terms.arith_leq_atom(t, num(n - 1))])
# no two queens in the same column
ctx.assert_formula(Terms.distinct(q))
# no two queens on the same diagonal
for i in range(n):
    for j in range(i + 1, n):
        d = Terms.sub(q[i], q[j])
        ctx.assert_formula(Terms.arith_neq_atom(d, num(j - i)))
        ctx.assert_formula(Terms.arith_neq_atom(d, num(i - j)))

solutions = []
while True:
    status = ctx.check_context()
    if status != Status.SAT:
        break
    model = Model.from_context(ctx, 1)
    values = [model.get_value(t) for t in q]
    model.dispose()
    solutions.append(values)
    # exclude this solution: at least one output differs (a no-good over the outputs)
    ctx.assert_formula(Terms.yor([Terms.arith_neq_atom(t, num(v)) for t, v in zip(q, values)]))

print("Solutions:", len(solutions))
for s in solutions:
    print(s)
# UNSAT here proves the enumeration is complete
print("Final status:", "UNSAT" if status == Status.UNSAT else status)

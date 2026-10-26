# 3x3 magic square: the numbers 1..9, all different, every row, column and diagonal sums to 15.
from yices import Context, Model, Status, Terms, Types

INT = Types.int_type()
n, total = 3, 15

def num(v):
    return Terms.integer(v)

# one uninterpreted integer term per cell (a decision variable)
cell = [[Terms.new_uninterpreted_term(INT, f"c{i}{j}") for j in range(n)] for i in range(n)]
flat = [t for row in cell for t in row]

ctx = Context()
# every cell holds a number from 1 to 9
for t in flat:
    ctx.assert_formulas([Terms.arith_geq_atom(t, num(1)), Terms.arith_leq_atom(t, num(n * n))])
# all numbers different
ctx.assert_formula(Terms.distinct(flat))
# every row, column and both diagonals sum to 15
lines = [row for row in cell] + [[cell[i][j] for i in range(n)] for j in range(n)]
lines += [[cell[i][i] for i in range(n)], [cell[i][n - 1 - i] for i in range(n)]]
for line in lines:
    ctx.assert_formula(Terms.arith_eq_atom(Terms.sum(line), num(total)))

status = ctx.check_context()
print("Status:", "SAT" if status == Status.SAT else status)
if status == Status.SAT:
    model = Model.from_context(ctx, 1)          # read values only after SAT
    grid = [[model.get_value(t) for t in row] for row in cell]
    model.dispose()
    for row in grid:
        print(row)
    print("Row sums:", [sum(r) for r in grid])
ctx.dispose()

# Pigeonhole: 5 pigeons, 4 holes, no two pigeons share a hole. Infeasible; the status says so, nothing is raised.
from yices import Context, Status, Terms, Types

pigeons, holes = 5, 4
num = Terms.integer
hole = [Terms.new_uninterpreted_term(Types.int_type(), f"p{i}") for i in range(pigeons)]

ctx = Context()
for h in hole:
    ctx.assert_formulas([Terms.arith_geq_atom(h, num(1)), Terms.arith_leq_atom(h, num(holes))])
ctx.assert_formula(Terms.distinct(hole))

status = ctx.check_context()
names = {Status.SAT: "SAT", Status.UNSAT: "UNSAT", Status.UNKNOWN: "UNKNOWN", Status.INTERRUPTED: "INTERRUPTED"}
print("Status:", names.get(status, status))
if status == Status.UNSAT:
    print("No assignment exists (proven infeasible)")

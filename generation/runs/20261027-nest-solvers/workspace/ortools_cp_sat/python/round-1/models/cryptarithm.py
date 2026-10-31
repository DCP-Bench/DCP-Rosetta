import json
import sys

from ortools.sat.python import cp_model

with open(sys.argv[1]) as f:
    data = json.load(f)

addends = data["addends"]
total = data["sum"]
words = addends + [total]
letters = sorted({ch for w in words for ch in w})

model = cp_model.CpModel()
digit = {ch: model.new_int_var(0, 9, f"d_{ch}") for ch in letters}
model.add_all_different(list(digit.values()))

for w in words:
    if len(w) > 1:
        model.add(digit[w[0]] != 0)


def value_expr(word):
    return cp_model.LinearExpr.weighted_sum(
        [digit[ch] for ch in word],
        [10 ** (len(word) - 1 - i) for i in range(len(word))],
    )


model.add(sum(value_expr(a) for a in addends) == value_expr(total))

solver = cp_model.CpSolver()
status = solver.solve(model)
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print(json.dumps({"digits": {ch: solver.value(digit[ch]) for ch in letters}}))
elif status == cp_model.INFEASIBLE:
    print(json.dumps({"status": "unsatisfiable"}))
else:
    raise SystemExit(solver.status_name(status))

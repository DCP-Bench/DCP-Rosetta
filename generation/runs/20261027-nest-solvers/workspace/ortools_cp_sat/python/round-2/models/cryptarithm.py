import json
import sys

from ortools.sat.python import cp_model


def main():
    with open(sys.argv[1]) as f:
        data = json.load(f)
    words = list(data["addends"]) + [data["sum"]]
    letters = sorted({c for w in words for c in w})

    model = cp_model.CpModel()
    digit = {c: model.new_int_var(0, 9, f"digit_{c}") for c in letters}
    model.add_all_different(list(digit.values()))
    for w in words:
        if len(w) > 1:
            model.add(digit[w[0]] != 0)

    def number(word):
        n = len(word)
        return cp_model.LinearExpr.weighted_sum(
            [digit[c] for c in word], [10 ** (n - 1 - i) for i in range(n)])

    model.add(sum(number(w) for w in data["addends"]) == number(data["sum"]))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(json.dumps({"digits": {c: solver.value(digit[c]) for c in letters}}))
    elif status == cp_model.INFEASIBLE:
        print(json.dumps({"status": "unsatisfiable"}))
    else:
        print(solver.status_name(status), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

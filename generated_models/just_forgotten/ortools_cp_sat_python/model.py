# just_forgotten: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install ortools`):
#   python just_forgotten.py just_forgotten.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Find the bank account number Joe forgot. It uses each digit from 0 to n-1 once, and
    in each set of digits he tried, a given number of digits are in their correct position."""
    guesses = instance["sets"]                # guesses[k][i]: digit i of the k-th number Joe tried
    correct = instance["num_correct_digits"]  # how many digits of each guess are in the right place
    n = len(guesses[0])                       # the number of digits

    model = cp_model.CpModel()

    # x[i] is digit i of the account number.
    x = [model.new_int_var(0, n - 1, f"x_{i}") for i in range(n)]

    # The account number has each digit from 0 to n-1 exactly once.
    model.add_all_different(x)

    for k, guess in enumerate(guesses):
        # hits[i] is true when digit i of the account number is digit i of guess k.
        hits = []
        for i in range(n):
            hit = model.new_bool_var(f"hit_{k}_{i}")
            model.add(x[i] == guess[i]).only_enforce_if(hit)
            model.add(x[i] != guess[i]).only_enforce_if(~hit)
            hits.append(hit)
        # Guess k has exactly `correct` digits in the right position.
        model.add(sum(hits) == correct)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

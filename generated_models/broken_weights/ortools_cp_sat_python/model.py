# broken_weights: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install ortools`):
#   python broken_weights.py broken_weights.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A merchant's measuring weight of m pounds broke into n pieces, each a whole number
    of pounds. On a balance scale the pieces must weigh every whole load from 1 to m."""
    m = instance["m"]          # the total weight of the unbroken weight, in pounds
    n_pieces = instance["n"]   # the number of pieces it broke into

    model = cp_model.CpModel()

    # weights[j] is the weight of piece j, in pounds
    weights = [model.new_int_var(1, m, f"weights_{j}") for j in range(n_pieces)]

    # The pieces add up to the whole weight.
    model.add(sum(weights) == m)

    # Every load from 1 to m can be balanced. The load sits on the right pan, so the
    # pieces on the left pan minus the pieces on the right pan must equal the load.
    for load in range(1, m + 1):
        # the contributions of the pieces to the balance, in pounds
        signed = []
        for j in range(n_pieces):
            # left is true when piece j is on the left pan, right when it is on the right pan
            left = model.new_bool_var(f"left_{load}_{j}")
            right = model.new_bool_var(f"right_{load}_{j}")
            # A piece is on at most one pan.
            model.add_at_most_one([left, right])
            # term is one piece's contribution, in pounds
            term = model.new_int_var(-m, m, f"term_{load}_{j}")
            # A piece on the left pan adds its weight, on the right pan takes it away, and off the
            # scale adds nothing.
            model.add(term == weights[j]).only_enforce_if(left)
            model.add(term == -weights[j]).only_enforce_if(right)
            model.add(term == 0).only_enforce_if([~left, ~right])
            signed.append(term)
        model.add(sum(signed) == load)

    return model, {"weights": weights}


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

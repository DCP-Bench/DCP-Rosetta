# session3_kidney_exchange: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install ortools`):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

from ortools.sat.python import cp_model


def create_model(instance):
    """At a hospital, some people on the waiting list for a kidney transplant can
    donate to others. Maximize the number of people who receive a kidney."""
    n_people = instance["num_people"]    # the number of people
    compatible = instance["compatible"]  # compatible[i]: the people that person i can donate to

    model = cp_model.CpModel()

    # transplants[i][j] is true when person i donates a kidney to person j
    transplants = [[model.new_bool_var(f"transplant_{i}_{j}") for j in range(n_people)] for i in range(n_people)]

    for i in range(n_people):
        gives = sum(transplants[i])                                    # the number of kidneys person i donates
        receives = sum(transplants[k][i] for k in range(n_people))     # the number of kidneys person i receives
        # Nobody gives more than one kidney, and nobody receives more than one.
        model.add(gives <= 1)
        model.add(receives <= 1)
        # Anyone who gives a kidney must receive one.
        model.add(gives <= receives)
        # Donations go only to compatible people.
        for j in range(n_people):
            if j + 1 not in compatible[i]:
                model.add(transplants[i][j] == 0)

    # Maximize the number of kidneys given, which is the number of people receiving one.
    model.maximize(sum(transplants[i][j] for i in range(n_people) for j in range(n_people)))

    return model, {"transplants": transplants}


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

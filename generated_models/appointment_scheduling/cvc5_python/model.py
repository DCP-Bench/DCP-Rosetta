# appointment_scheduling: a cvc5 (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python appointment_scheduling.py appointment_scheduling.json

import cvc5.pythonic as c5


def create_model(instance):
    """Schedule people into interview slots based on their free-busy schedules:
    every person gets exactly one slot in which they are free, and every slot
    gets exactly one person."""
    free = instance["m"]  # free[i][j] is 1 when person i is free in slot j, else 0
    n = len(free)         # the number of people, which is also the number of slots

    # x[i][j] is true when person i is interviewed in slot j
    x = [[c5.Bool(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    solver = c5.Solver()

    # Each person has exactly one interview slot.
    solver.add([c5.Sum([c5.If(xij, 1, 0) for xij in row]) == 1 for row in x])

    # Each slot has exactly one person.
    solver.add([c5.Sum([c5.If(x[i][j], 1, 0) for i in range(n)]) == 1 for j in range(n)])

    # A person is only interviewed in a slot in which they are free.
    solver.add([c5.Not(x[i][j]) for i in range(n) for j in range(n) if free[i][j] == 0])

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

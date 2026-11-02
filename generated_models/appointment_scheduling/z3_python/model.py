# appointment_scheduling: a Z3 (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python appointment_scheduling.py appointment_scheduling.json

import z3


def create_model(instance):
    """Schedule people into interview slots based on their free-busy schedules:
    every person gets exactly one slot in which they are free, and every slot
    gets exactly one person."""
    free = instance["m"]  # free[i][j] is true when person i is free in slot j
    n = len(free)         # the number of people, which is also the number of slots

    # booked[i][j] is true when person i is assigned to slot j
    booked = [[z3.Bool(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    # taken[i][j] is 1 when person i is assigned to slot j, else 0
    taken = [[z3.If(booked[i][j], 1, 0) for j in range(n)] for i in range(n)]

    solver = z3.Solver()
    # Each person's slot is one in which they are free.
    solver.add([z3.Sum([free[i][j] * taken[i][j] for j in range(n)]) == 1 for i in range(n)])
    # Each person is assigned to exactly one slot.
    solver.add([z3.Sum(taken[i]) == 1 for i in range(n)])
    # Each slot gets exactly one person.
    solver.add([z3.Sum([taken[j][i] for j in range(n)]) == 1 for i in range(n)])

    return solver, {"x": booked}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

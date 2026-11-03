# session3_kidney_exchange: an Exact (Python) model from DCP Rosetta.
# Download the `session3_kidney_exchange.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python session3_kidney_exchange.py session3_kidney_exchange.json

from exact import Exact


def create_model(instance):
    """At a hospital, n people wait for a kidney transplant, and some of them can
    donate to others. Choose the donations so that anyone who gives a kidney also
    receives one and nobody receives more than one. Maximize the number of people
    who receive a kidney."""
    n_people = instance["num_people"]    # the number of people on the waiting list, numbered 1 up to n_people
    compatible = instance["compatible"]  # compatible[i]: the people (1-based) that person i + 1 can donate to

    solver = Exact()

    # Exact identifies its variables by name.
    # transplants[i][j] is 1 when person i donates a kidney to person j, and 0 otherwise.
    # Pairs that are not compatible are fixed to 0.
    transplants = [[f"transplant_{i}_{j}" for j in range(n_people)] for i in range(n_people)]
    for i in range(n_people):
        for j in range(n_people):
            solver.addVariable(transplants[i][j], 0, 1 if (j + 1) in compatible[i] else 0)

    for i in range(n_people):
        gives = [(1, transplants[i][j]) for j in range(n_people)]
        receives = [(1, transplants[j][i]) for j in range(n_people)]
        # Person i donates at most one kidney.
        solver.addConstraint(gives, False, 0, True, 1)
        # Person i receives at most one kidney.
        solver.addConstraint(receives, False, 0, True, 1)
        # Anyone who donates a kidney also receives one.
        solver.addConstraint(gives + [(-c, name) for c, name in receives], False, 0, True, 0)

    # The number of kidneys given is the number of people who receive one.
    solver.setObjective([(1, transplants[i][j]) for i in range(n_people) for j in range(n_people)], minimize=False)

    return solver, {"transplants": transplants}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

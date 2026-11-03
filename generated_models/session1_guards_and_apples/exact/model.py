# session1_guards_and_apples: an Exact (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

from exact import Exact


def create_model(instance):
    """A boy passes through a number of gates, each with a guard, to give an apple
    to a girl. At each gate he gives the guard half of his apples plus one, always a
    whole number of apples, and has none left after giving the girl her apple."""
    n_gates = instance["num_gates"]  # the number of gates, and so of guards

    solver = Exact()

    # Exact identifies its variables by name.
    # apples[i] is how many apples the boy has before gate i. The last entry is how
    # many he has after the last gate: the one apple he gives the girl.
    apples = [f"apples_{i}" for i in range(n_gates + 1)]
    for name in apples[:-1]:
        solver.addVariable(name, 0, 100)
    solver.addVariable(apples[-1], 1, 1)

    # At each gate he gives the guard half of his apples plus one, so the apples
    # before the gate are twice the apples after it, plus two.
    for gate in range(n_gates):
        solver.addConstraint([(1, apples[gate]), (-2, apples[gate + 1])], True, 2, True, 2)

    return solver, {"apples": apples}


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

# session1_guards_and_apples: a cvc5 (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

import cvc5.pythonic as c5


def create_model(instance):
    """A boy passes through a number of gates to give an apple to a girl. At
    each gate he bribes the guard with half of his apples plus one, always a
    whole number of apples, and after the girl gets her apple he has none left."""
    num_gates = instance["num_gates"]  # the number of gates, each with a guard

    # apples[i] is the number of apples the boy has before gate i; the last
    # entry is the number he has after the last gate.
    apples = [c5.Int(f"apples_{i}") for i in range(num_gates + 1)]

    solver = c5.Solver()

    # He never has a negative number of apples.
    solver.add([a >= 0 for a in apples])

    # After the last gate he has one apple left, the one he gives the girl.
    solver.add(apples[num_gates] == 1)

    # At each gate he gives half of his apples plus one, so before the gate he
    # had twice what remains after it, plus two.
    for i in range(num_gates):
        solver.add(apples[i] == 2 * (apples[i + 1] + 1))

    return solver, {"apples": apples}


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

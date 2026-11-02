# session1_guards_and_apples: a Z3 (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

import z3


def create_model(instance):
    """A boy passes through a number of gates to give an apple to a girl. He
    bribes each guard with half of his apples plus one, always a whole number
    of apples, and has none left after giving the girl her apple."""
    num_gates = instance["num_gates"]  # how many gates, each with a guard

    # apples[i] is the number of apples the boy has before gate i; the last entry
    # is the number he has after the last gate.
    apples = [z3.Int(f"apples_{i}") for i in range(num_gates + 1)]

    solver = z3.Solver()

    # The boy never has more than 100 apples, and never a negative number.
    solver.add([z3.And(0 <= count, count <= 100) for count in apples])

    # After the last gate he has one apple left, which he gives to the girl.
    solver.add(apples[num_gates] == 1)

    # At each gate he gives the guard half of his apples plus one. So the apples
    # before a gate are twice the apples after it, plus two.
    solver.add([apples[i] == 2 * (apples[i + 1] + 1) for i in range(num_gates)])

    return solver, {"apples": apples}


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

# session1_guards_and_apples: a SCIP (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

from pyscipopt import Model


def create_model(instance):
    """A boy has to give an apple to a girl. He passes a number of gates, each with a guard,
    and bribes each guard with half of his apples plus one. A bribe must be a whole number
    of apples, and after the last gate he has only the one apple he gives the girl, so he
    has no apples left. Find how many apples he has before each gate and after the last one."""
    num_gates = instance["num_gates"]  # the number of gates, each with a guard

    model = Model("guards_and_apples")

    # The most apples he can have at any point. The equations below force apples[i] to be
    # 3 * 2 ** (num_gates - i) - 2: going back one gate doubles the count and adds 2, starting
    # from 1 apple after the last gate. So every count is at most 3 * 2 ** num_gates. This bound
    # follows from the equations, not from the problem statement.
    max_apples = 3 * 2 ** num_gates

    # apples[i] is the number of apples he has before gate i, and apples[num_gates] the number
    # he has after the last gate. A count of apples cannot be negative.
    apples = [model.addVar(f"apples_{i}", vtype="I", lb=0, ub=max_apples) for i in range(num_gates + 1)]

    # bribe[i] is the number of apples he gives the guard at gate i. It is a whole number
    # because the problem says the bribe is a whole number of apples.
    bribe = [model.addVar(f"bribe_{i}", vtype="I", lb=0, ub=max_apples) for i in range(num_gates)]

    # After the last gate he keeps only the one apple he gives the girl, so none are left.
    model.addCons(apples[num_gates] == 1)

    for i in range(num_gates):
        # The bribe is half his apples plus one. Python's // is not available on variables, so
        # "half" is written as 2 * bribe = apples + 2: this needs apples[i] to be even, which is
        # the statement's requirement that the bribe is a whole number.
        model.addCons(2 * bribe[i] == apples[i] + 2)

        # He hands over the bribe and keeps the rest for the next gate.
        model.addCons(apples[i + 1] == apples[i] - bribe[i])

    return model, {"apples": apples}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

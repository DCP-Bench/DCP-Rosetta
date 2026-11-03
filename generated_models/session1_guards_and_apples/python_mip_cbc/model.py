# session1_guards_and_apples: a Python-MIP (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

import mip


def create_model(instance):
    """A boy passes a number of gates. At each gate he gives the guard half of
    his apples plus one, which is always a whole number of apples. After the
    last gate he gives the girl one apple and has none left. Find how many
    apples he has before each gate and after the last one."""
    num_gates = instance["num_gates"]  # how many gates, each with a guard

    # Upper bound on every count of apples. Each gate leaves fewer apples than it
    # finds, so the counts shrink from the first gate to the end.
    ub = 2 ** (num_gates + 2)

    model = mip.Model(solver_name="CBC")

    # apples[i] is the number of apples the boy has before gate i. The last entry is
    # the number after the last gate: the one apple he then gives the girl.
    apples = [model.add_var(f"apples_{i}", lb=0, ub=ub, var_type=mip.INTEGER) for i in range(num_gates)]
    apples.append(model.add_var(f"apples_{num_gates}", lb=1, ub=1, var_type=mip.INTEGER))

    # At each gate he gives half of his apples plus one, so before the gate he had
    # twice the number left after it, plus 2.
    for i in range(num_gates):
        model += apples[i] == 2 * (apples[i + 1] + 1)

    # No objective: the counts that satisfy the gates answer the puzzle.
    return model, {"apples": apples}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

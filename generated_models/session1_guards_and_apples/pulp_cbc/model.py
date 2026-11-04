# session1_guards_and_apples: a PuLP (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

import pulp


def create_model(instance):
    """A boy passes through a number of gates to give an apple to a girl. At each
    gate he bribes the guard with half of his apples plus one, always a whole number
    of apples, and he has no apples left after giving the girl her apple."""
    num_gates = instance["num_gates"]  # how many gates, each with a guard, the boy passes

    problem = pulp.LpProblem("guards_and_apples", pulp.LpMinimize)

    # apples[i] is the number of apples the boy has before gate i. The last entry is
    # the number left after the last gate, which is the one apple he gives the girl.
    # Each count is at most 100.
    apples = [pulp.LpVariable(f"apples_{i}", 0, 100, cat="Integer") for i in range(num_gates)]
    apples.append(pulp.LpVariable(f"apples_{num_gates}", 1, 1, cat="Integer"))

    # At each gate he pays the guard half of his apples plus one, so before the gate
    # he had twice what is left after it, plus 2.
    for i in range(num_gates):
        problem += apples[i] == 2 * (apples[i + 1] + 1)

    # No objective: the gates fix every count.
    return problem, {"apples": apples}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

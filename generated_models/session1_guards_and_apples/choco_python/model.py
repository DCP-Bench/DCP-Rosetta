# session1_guards_and_apples: a Choco-solver (Python) model from DCP Rosetta.
# Download the `session1_guards_and_apples.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python session1_guards_and_apples.py session1_guards_and_apples.json

from pychoco.model import Model


def create_model(instance):
    """A boy passes through a number of gates to give an apple to a girl. At
    each gate he gives the guard half of his apples plus one, always a whole
    number of apples, and he has none left after giving the girl her apple."""
    num_gates = instance["num_gates"]  # how many gates, each with a guard

    model = Model()

    # apples[i] is the number of apples the boy has before gate i, and apples[num_gates]
    # the number after the last gate. He never has more than 100 apples.
    apples = [model.intvar(0, 100, name=f"apples_{i}") for i in range(num_gates)]
    # After the last gate he has one apple left, which he gives to the girl.
    apples.append(model.intvar(1, 1, name=f"apples_{num_gates}"))

    # At each gate he gives the guard half of his apples plus one, so before the gate
    # he has twice what he has after it, plus two.
    for i in range(num_gates):
        model.scalar([apples[i], apples[i + 1]], [1, -2], "=", 2).post()

    return model, {"apples": apples}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")

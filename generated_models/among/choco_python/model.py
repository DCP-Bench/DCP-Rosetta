# among: a Choco-solver (Python) model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python among.py among.json

from pychoco.model import Model


def create_model(instance):
    """Exactly m of the values in x take one of the values in v. Every value in x
    is at least 0 and at most 7."""
    n = instance["n"]  # the number of values in x
    m = instance["m"]  # how many values in x must take a value from v
    v = instance["v"]  # the values that are counted

    model = Model()

    # x[i] is the value at position i, from 0 to 7.
    x = [model.intvar(0, 7, name=f"x{i}") for i in range(n)]

    # hits: one mark for each position and each value in v, true when the position takes that value.
    hits = []
    for variable in x:
        for value in v:
            hits.append(model.arithm(variable, "=", value).reify())

    # Exactly m marks are true, so exactly m positions take a value from v.
    model.sum(hits, "=", m).post()

    return model, {"x": x}, None


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

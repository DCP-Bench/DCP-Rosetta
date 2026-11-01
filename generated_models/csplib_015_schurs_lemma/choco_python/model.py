# csplib_015_schurs_lemma: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

from pychoco.model import Model


def create_model(instance):
    """Schur's lemma: put n balls labelled 1 to n into c boxes so that no triple of balls
    x, y, z with x + y = z lies all in one box."""
    n = instance["n"]  # the number of balls, labelled 1 to n
    c = instance["c"]  # the number of boxes, labelled 1 to c

    model = Model()

    # balls[k - 1] is the box that ball k goes in
    balls = [model.intvar(1, c, name=f"ball_{k}") for k in range(1, n + 1)]

    # No triple x, y, z with x + y = z has all three balls in one box. One of the three
    # pairs must be in different boxes; when x = y the pair is one ball, so it never is.
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            model.or_([
                model.arithm(balls[x - 1], "!=", balls[y - 1]),
                model.arithm(balls[x - 1], "!=", balls[z - 1]),
                model.arithm(balls[y - 1], "!=", balls[z - 1]),
            ]).post()

    return model, {"balls": balls}, None


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

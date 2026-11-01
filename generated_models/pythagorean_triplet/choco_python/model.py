# pythagorean_triplet: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install pychoco numpy`) with:
#   python pythagorean_triplet.py

from pychoco.model import Model


def create_model(instance):
    """Find the Pythagorean triplet a, b, c of natural numbers with a^2 + b^2 = c^2
    whose three members add up to 1000."""
    model = Model()

    # a, b, c: the three members of the triplet. No member exceeds the other two together,
    # so each is at most half of 1000, that is at most 500.
    a = model.intvar(1, 500, name="a")
    b = model.intvar(1, 500, name="b")
    c = model.intvar(1, 500, name="c")

    # The three members add up to 1000.
    model.scalar([a, b, c], [1, 1, 1], "=", 1000).post()

    # aa, bb, cc: the squares of a, b and c.
    aa = model.intvar(1, 500 * 500, name="aa")
    bb = model.intvar(1, 500 * 500, name="bb")
    cc = model.intvar(1, 500 * 500, name="cc")
    model.square(aa, a).post()
    model.square(bb, b).post()
    model.square(cc, c).post()

    # The squares satisfy a^2 + b^2 = c^2.
    model.scalar([aa, bb, cc], [1, 1, -1], "=", 0).post()

    return model, {"a": a, "b": b, "c": c}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
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

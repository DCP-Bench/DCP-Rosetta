# abbots_puzzle: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install pychoco numpy`) with:
#   python abbots_puzzle.py

from pychoco.model import Model


def create_model(instance):
    """Share 100 bushels of corn among 100 people: each man gets three bushels, each
    woman two and each child half a bushel, and there are five times as many women
    as men. Find the number of men, women and children."""
    model = Model()

    # The number of men.
    men = model.intvar(0, 100, name="men")
    # The number of women.
    women = model.intvar(0, 100, name="women")
    # The number of children.
    children = model.intvar(0, 100, name="children")

    # There are 100 people.
    model.scalar([men, women, children], [1, 1, 1], "=", 100).post()
    # The bushels add up to 100. Counted in half bushels (a man 6, a woman 4, a child 1),
    # so every coefficient is a whole number and the total is 200.
    model.scalar([men, women, children], [6, 4, 1], "=", 200).post()
    # There are five times as many women as men.
    model.scalar([men, women], [5, -1], "=", 0).post()

    return model, {"men": men, "women": women, "children": children}, None


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

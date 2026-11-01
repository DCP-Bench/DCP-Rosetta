# dinner: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install pychoco numpy`) with:
#   python dinner.py

from pychoco.model import Model


def create_model(instance):
    """Twenty people go to dinner: grandparents at $3 each, parents at $2 each and
    children at $0.50 each. Take 1 to 6 grandparents, 1 to 10 parents and 1 to 40
    children so that the dinner costs $20. How many of each go?"""
    model = Model()

    # The number of grandparents, parents and children going to dinner
    grandparents = model.intvar(1, 6, name="grandparents")
    parents = model.intvar(1, 10, name="parents")
    children = model.intvar(1, 40, name="children")

    # The bill is $20, which is 40 half dollars. In half dollars a grandparent
    # costs 6, a parent 4 and a child 1.
    model.scalar([grandparents, parents, children], [6, 4, 1], "=", 40).post()
    # There are 20 people at dinner.
    model.sum([grandparents, parents, children], "=", 20).post()

    return model, {"grandparents": grandparents, "parents": parents, "children": children}, None


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

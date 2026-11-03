# giant_cat_army: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install pychoco numpy`) with:
#   python giant_cat_army.py

from pychoco.model import Model


def create_model(instance):
    """Build a list that starts with 0, where each next number is the previous one
    plus 5, plus 7, or its square root. The numbers are distinct integers of at most
    60, the list has 24 numbers, ends with 14, and has 2 before 10."""
    max_value = 60  # the largest number allowed in the list
    n_numbers = 24  # how many numbers the list has

    model = Model()

    # x[i] is the i-th number of the list. The first is 0 and the last is 14.
    x = ([model.intvar(0, 0, name="x_0")]
         + [model.intvar(0, max_value, name=f"x_{i}") for i in range(1, n_numbers - 1)]
         + [model.intvar(14, 14, name=f"x_{n_numbers - 1}")])

    # The numbers are all different.
    model.all_different(x).post()

    # Pairs (a, b) where b can follow a: b = a + 5, b = a + 7, or a = b * b.
    steps = set()
    for v in range(max_value + 1):
        if v + 5 <= max_value:
            steps.add((v, v + 5))
        if v + 7 <= max_value:
            steps.add((v, v + 7))
        if v * v <= max_value:
            steps.add((v * v, v))
    steps = [list(pair) for pair in sorted(steps)]

    # Each number follows the one before it by an allowed step.
    for i in range(n_numbers - 1):
        model.table([x[i], x[i + 1]], steps).post()

    # The numbers 2 and 10, as variables that can be looked up in the list.
    two = model.intvar(2, 2, name="two")
    ten = model.intvar(10, 10, name="ten")

    # The places of 2 and 10 in the list.
    pos_2 = model.intvar(1, n_numbers - 1, name="pos_2")
    pos_10 = model.intvar(1, n_numbers - 1, name="pos_10")
    model.element(two, x, pos_2).post()
    model.element(ten, x, pos_10).post()

    # 2 comes before 10.
    model.arithm(pos_2, "<", pos_10).post()

    return model, {"x": x}, None


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

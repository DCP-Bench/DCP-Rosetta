# giant_cat_army: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install exact numpy`) with:
#   python giant_cat_army.py

from exact import Exact


def create_model(instance):
    """Start from 0 and build a list of 24 numbers. Each number is the one before it plus 5,
    plus 7, or the square root of the one before it. The numbers are distinct integers of at
    most 60, the list ends with 14, and 2 appears before 10."""
    max_value = 60  # the largest number allowed in the list
    n_numbers = 24  # the length of the list
    goal = 14       # the last number of the list

    solver = Exact()

    # Exact identifies its variables by name.
    # number[i] is the i-th number of the list.
    number = [f"number_{i}" for i in range(n_numbers)]
    # The first number is 0 and the last is the goal.
    bounds = {0: (0, 0), n_numbers - 1: (goal, goal)}
    for i, name in enumerate(number):
        solver.addVariable(name, *bounds.get(i, (0, max_value)))

    # is_value[i][v] is 1 when the i-th number is v, and 0 when not.
    is_value = [{v: f"is_{i}_{v}" for v in range(max_value + 1)} for i in range(n_numbers)]
    for i in range(n_numbers):
        for v in range(max_value + 1):
            solver.addVariable(is_value[i][v], 0, 1)
        # Each position holds exactly one number.
        solver.addConstraint([(1, is_value[i][v]) for v in range(max_value + 1)], True, 1, True, 1)
        # The i-th number is the value v for which is_value[i][v] is 1.
        solver.addConstraint([(v, is_value[i][v]) for v in range(1, max_value + 1)] + [(-1, number[i])],
                             True, 0, True, 0)

    # No number appears twice in the list.
    for v in range(max_value + 1):
        solver.addConstraint([(1, is_value[i][v]) for i in range(n_numbers)], False, 0, True, 1)

    # Each number follows from the one before it: the next number is that number plus 5,
    # plus 7, or its square root.
    for i in range(n_numbers - 1):
        for v in range(max_value + 1):
            next_values = [w for w in (v + 5, v + 7) if w <= max_value]
            root = int(v ** 0.5)
            if root * root == v:
                next_values.append(root)
            solver.addConstraint([(1, is_value[i + 1][w]) for w in next_values] + [(-1, is_value[i][v])],
                                 True, 0, False, 0)

    # 10 is in the list.
    solver.addConstraint([(1, is_value[j][10]) for j in range(n_numbers)], True, 1, False, 0)
    # Each 10 in the list has a 2 before it.
    for j in range(1, n_numbers):
        solver.addConstraint([(1, is_value[i][2]) for i in range(1, j)] + [(-1, is_value[j][10])],
                             True, 0, False, 0)

    # The numbers of the list, in order.
    return solver, {"x": number}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

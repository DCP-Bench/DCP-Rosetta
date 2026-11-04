# circling_squares: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install pulp numpy`) with:
#   python circling_squares.py

import pulp


def create_model(instance):
    """Circling the squares: place a different number in each of ten squares of a circle, so
    that the sum of the squares of two adjacent numbers equals the sum of the squares of the two
    numbers diametrically opposite them. Four of the numbers are given."""
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]  # the squares in order round the circle
    given = {"A": 16, "B": 2, "F": 8, "G": 14}                  # the numbers placed as examples
    values = range(1, 100)                                      # no number needs more than two figures

    problem = pulp.LpProblem("circling_squares", pulp.LpMinimize)

    # is_value[s][v] is 1 when square s holds the number v, and 0 when not.
    # A given square has only its given number as a choice.
    is_value = {}
    for s in names:
        choices = [given[s]] if s in given else values
        is_value[s] = {v: pulp.LpVariable(f"is_{s}_{v}", cat="Binary") for v in choices}

    # Each square holds exactly one number.
    for s in names:
        problem += pulp.lpSum(is_value[s].values()) == 1

    # number[s] is the number in square s, and square[s] is its square.
    number = {s: pulp.lpSum(v * b for v, b in is_value[s].items()) for s in names}
    square = {s: pulp.lpSum(v * v * b for v, b in is_value[s].items()) for s in names}

    # Each number is in at most one square.
    for v in values:
        problem += pulp.lpSum(is_value[s][v] for s in names if v in is_value[s]) <= 1

    # The two adjacent squares A and B have the same sum of squares as the two opposite squares
    # F and G, and so on round the circle.
    for first, second, third, fourth in [
        ("A", "B", "F", "G"),
        ("B", "C", "G", "H"),
        ("C", "D", "H", "I"),
        ("D", "E", "I", "K"),
        ("E", "F", "K", "A"),
    ]:
        problem += square[first] + square[second] == square[third] + square[fourth]

    return problem, number


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

# session5_hardy_1729_square: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install pulp numpy`) with:
#   python session5_hardy_1729_square.py

import pulp


def create_model(instance):
    """Find four different numbers between 1 and 100 such that the sum of the squares
    of the first two equals the sum of the squares of the last two: a^2 + b^2 = c^2 + d^2."""
    values = range(1, 101)  # each number is between 1 and 100
    names = ["a", "b", "c", "d"]  # the four numbers

    problem = pulp.LpProblem("session5_hardy_1729_square", pulp.LpMinimize)  # no objective: any four numbers that fit are an answer

    # is_value[x][v] is 1 when number x is v.
    is_value = {x: {v: pulp.LpVariable(f"{x}_is_{v}", cat="Binary") for v in values}
                for x in names}

    # Each number takes exactly one value.
    for x in names:
        problem += pulp.lpSum(is_value[x].values()) == 1

    # number[x] is the value of x, and square[x] is its square, both read off the choice of value.
    number = {x: pulp.lpSum(v * var for v, var in is_value[x].items()) for x in names}
    square = {x: pulp.lpSum(v * v * var for v, var in is_value[x].items()) for x in names}

    # The four numbers are all different: no value is taken by more than one of them.
    for v in values:
        problem += pulp.lpSum(is_value[x][v] for x in names) <= 1

    # The squares of a and b add up to the squares of c and d.
    problem += square["a"] + square["b"] == square["c"] + square["d"]

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

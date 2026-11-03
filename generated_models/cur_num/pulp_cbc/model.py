# cur_num: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install pulp numpy`) with:
#   python cur_num.py

import math

import pulp


def create_model(instance):
    """The number 48 is peculiar: adding 1 to it gives a square number, and adding 1
    to its half gives a square number too. Find another number between 1 and 10000
    with this peculiarity."""
    top = 10000    # the largest number the puzzle considers
    example = 48   # the peculiar number given in the puzzle; the answer is another one

    problem = pulp.LpProblem("cur_num", pulp.LpMinimize)  # the puzzle asks for any such number

    # The peculiar number that is sought, and half of it
    peculiar = pulp.LpVariable("peculiar", 1, top, cat="Integer")
    half = pulp.LpVariable("half", 1, top, cat="Integer")

    # The roots run up to 100, since 101 squared is above 10000.
    roots = range(1, math.isqrt(top) + 1)
    # root_a[r] is 1 when peculiar + 1 is the square of r
    root_a = {r: pulp.LpVariable(f"root_a_{r}", cat="Binary") for r in roots}
    # root_b[r] is 1 when half + 1 is the square of r
    root_b = {r: pulp.LpVariable(f"root_b_{r}", cat="Binary") for r in roots}
    problem += pulp.lpSum(root_a.values()) == 1
    problem += pulp.lpSum(root_b.values()) == 1

    # Adding 1 to the number gives a square number.
    problem += peculiar + 1 == pulp.lpSum(r * r * var for r, var in root_a.items())

    # The number is twice its half, and adding 1 to the half gives a square number.
    problem += peculiar == 2 * half
    problem += half + 1 == pulp.lpSum(r * r * var for r, var in root_b.items())

    # The number is not 48: it lies below 48 or above it.
    above = pulp.LpVariable("above", cat="Binary")  # 1 when the number is above 48, 0 when below
    problem += peculiar <= example - 1 + top * above
    problem += peculiar >= example + 1 - top * (1 - above)

    return problem, {"peculiar": peculiar}


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

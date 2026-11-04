# dinner: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install pulp numpy`) with:
#   python dinner.py

import pulp


def create_model(instance):
    """Twenty people go out to dinner, grandparents, parents and children, and
    the bill is $20: how many of each go?"""
    problem = pulp.LpProblem("dinner", pulp.LpMinimize)

    # The number of grandparents (1 to 6), parents (1 to 10) and children (1 to 40) at dinner
    grandparents = pulp.LpVariable("grandparents", 1, 6, cat="Integer")
    parents = pulp.LpVariable("parents", 1, 10, cat="Integer")
    children = pulp.LpVariable("children", 1, 40, cat="Integer")

    # Prices in half dollars, so that the child's $0.50 is a whole number: a
    # grandparent is 6, a parent 4 and a child 1.
    # The bill is $20, which is 40 half dollars.
    problem += 6 * grandparents + 4 * parents + children == 40

    # There are 20 people in total.
    problem += grandparents + parents + children == 20

    return problem, {
        "grandparents": grandparents, "parents": parents, "children": children,
    }


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

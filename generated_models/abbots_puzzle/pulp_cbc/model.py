# abbots_puzzle: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install pulp numpy`) with:
#   python abbots_puzzle.py

import pulp


def create_model(instance):
    """100 bushels of corn are distributed among 100 people: each man receives
    three bushels, each woman two and each child half a bushel, and there are
    five times as many women as men. Find the number of men, women and children."""
    problem = pulp.LpProblem("abbots", pulp.LpMinimize)

    # The number of men, women and children.
    men = pulp.LpVariable("men", 0, 100, cat="Integer")
    women = pulp.LpVariable("women", 0, 100, cat="Integer")
    children = pulp.LpVariable("children", 0, 100, cat="Integer")

    # There are 100 people.
    problem += men + women + children == 100

    # The bushels add up to 100. Counting in half bushels, a man gets 6, a woman 4 and a child 1, 200 in all.
    problem += 6 * men + 4 * women + children == 200

    # There are five times as many women as men.
    problem += women == 5 * men

    return problem, {"men": men, "women": women, "children": children}


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

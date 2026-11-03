# contracting_costs: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install pulp numpy`) with:
#   python contracting_costs.py

import pulp


def create_model(instance):
    """A contractor pays six tradesmen in pairs, a known sum for each pair's
    two services together. What does each man charge for his services?"""
    # The six tradesmen.
    names = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]
    # The pairs of tradesmen the contractor pays, with the sum in dollars for each pair.
    pairs = [
        ("paper_hanger", "painter", 1100),
        ("painter", "plumber", 1700),
        ("plumber", "electrician", 1100),
        ("electrician", "carpenter", 3300),
        ("carpenter", "mason", 5300),
        ("mason", "painter", 3200),
    ]
    # No man charges more than the largest sum paid to a pair.
    largest = max(bill for _, _, bill in pairs)

    problem = pulp.LpProblem("contracting", pulp.LpMinimize)

    # charge[name] is what that tradesman charges, in whole dollars, from 1 to the largest sum.
    charge = {name: pulp.LpVariable(name, 1, largest, cat="Integer") for name in names}

    # The two men in each pair together charge the sum paid to that pair.
    for first, second, bill in pairs:
        problem += charge[first] + charge[second] == bill

    return problem, charge


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

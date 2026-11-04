# five_brigands: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install pulp numpy`) with:
#   python five_brigands.py

import pulp


def create_model(instance):
    """Five Spanish brigands, Alfonso, Benito, Carlos, Diego and Esteban, captured
    exactly 200 doubloons altogether. If Alfonso had twelve times as many, Benito
    three times as many, Carlos the same, Diego half as many and Esteban a third as
    many, they would still have 200 doubloons altogether. Each brigand has at least
    one doubloon. How many doubloons has each?"""
    problem = pulp.LpProblem("five_brigands", pulp.LpMinimize)

    # A, B, C, D and E are the doubloons of Alfonso, Benito, Carlos, Diego and Esteban
    x = {name: pulp.LpVariable(name, 1, 200, cat="Integer") for name in ["A", "B", "C", "D", "E"]}

    # Together they have 200 doubloons.
    problem += pulp.lpSum(x.values()) == 200

    # With the changed amounts they still have 200 doubloons. The equation is multiplied by 6
    # so that the halves and thirds become whole numbers.
    problem += 72 * x["A"] + 18 * x["B"] + 6 * x["C"] + 3 * x["D"] + 2 * x["E"] == 6 * 200

    return problem, x


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

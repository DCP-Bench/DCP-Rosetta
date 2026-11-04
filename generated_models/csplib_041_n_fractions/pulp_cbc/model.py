# csplib_041_n_fractions: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install pulp numpy`) with:
#   python csplib_041_n_fractions.py

from itertools import permutations

import pulp


def create_model(instance):
    """Find distinct non-zero digits A to I such that A / BC + D / EF + G / HI = 1, where BC,
    EF and HI are the two-digit numbers formed by B and C, E and F, and H and I."""
    digits = range(1, 10)  # the non-zero digits
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]  # output names of the nine digits, A to I

    problem = pulp.LpProblem("n_fractions", pulp.LpMinimize)  # the puzzle asks for digits only: no objective

    # Each way of choosing three different digits a, b, c for one fraction a / (10b + c)
    triples = list(permutations(digits, 3))
    # term[k][t] is 1 when fraction k is made of the digits t, and 0 when not
    term = [{t: pulp.LpVariable(f"term_{k}_{t[0]}{t[1]}{t[2]}", cat="Binary") for t in triples}
            for k in range(3)]

    # Each of the three fractions is made of exactly one of these triples.
    for k in range(3):
        problem += pulp.lpSum(term[k].values()) == 1

    # The nine digits are all different: each digit appears in exactly one place.
    for v in digits:
        problem += pulp.lpSum(var for k in range(3) for t, var in term[k].items()
                              if v in t) == 1

    # A / BC + D / EF + G / HI = 1
    problem += pulp.lpSum(t[0] / (10 * t[1] + t[2]) * var
                          for k in range(3) for t, var in term[k].items()) == 1

    # Each digit is read off the chosen fractions: the numerator, then the two digits of the denominator.
    outputs = {}
    for k in range(3):
        for place in range(3):
            outputs[names[3 * k + place]] = pulp.lpSum(t[place] * var
                                                       for t, var in term[k].items())
    return problem, outputs


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

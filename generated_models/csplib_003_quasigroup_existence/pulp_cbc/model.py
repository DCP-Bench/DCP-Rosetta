# csplib_003_quasigroup_existence: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

import pulp


def create_model(instance):
    """QG3.m quasigroup existence: find an order m quasigroup, a Latin square of size
    m with every element once in each row and column, such that (a*b)*(b*a) = a."""
    m = instance["m"]            # the order of the quasigroup, the size of the table
    elements = range(m)          # the elements 0 to m-1

    problem = pulp.LpProblem("qg3", pulp.LpMinimize)

    # maps(a, b, k, l) is 1 when a*b is k and b*a is l. The QG3 rule says that k*l is a and
    # l*k is b, so the same fact read from the cells (b, a), (k, l) and (l, k) is the same
    # variable.
    shared = {}  # the variables made so far, under the smallest of the four readings of their fact

    def maps(a, b, k, l):
        key = min((a, b, k, l), (k, l, a, b), (b, a, l, k), (l, k, b, a))
        if key not in shared:
            shared[key] = pulp.LpVariable("maps_%d_%d_%d_%d" % key, cat="Binary")
        return shared[key]

    # times_is(a, b, k) is 1 when a*b is k.
    def times_is(a, b, k):
        return pulp.lpSum(maps(a, b, k, l) for l in elements)

    # Each pair (a, b) has exactly one product a*b, which fixes the reverse product b*a too.
    for a in elements:
        for b in elements:
            problem += pulp.lpSum(maps(a, b, k, l) for k in elements for l in elements) == 1

    for k in elements:
        # In every row, each element occurs once.
        for a in elements:
            problem += pulp.lpSum(times_is(a, b, k) for b in elements) == 1
        # In every column, each element occurs once.
        for b in elements:
            problem += pulp.lpSum(times_is(a, b, k) for a in elements) == 1

    # quasigroup[a][b] is the product a*b.
    quasigroup = [[pulp.lpSum(k * times_is(a, b, k) for k in elements) for b in elements]
                  for a in elements]
    return problem, {"quasigroup": quasigroup}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

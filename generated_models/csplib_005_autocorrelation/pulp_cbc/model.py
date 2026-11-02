# csplib_005_autocorrelation: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

import pulp


def create_model(instance):
    """Choose a binary sequence of length n, each value +1 or -1, whose periodic
    autocorrelations are as small as possible. The energy is the sum of the squares of
    the autocorrelations C_1 to C_(n-1), where C_k adds up S_i * S_((i+k) mod n) over all i."""
    n = instance["n"]  # the length of the sequence

    problem = pulp.LpProblem("autocorrelation", pulp.LpMinimize)

    # bit[i] is 1 when the value at position i is +1, and 0 when it is -1
    bit = [pulp.LpVariable(f"bit_{i}", cat="Binary") for i in range(n)]

    # S_i, the value at position i: +1 or -1
    sequence = [2 * bit[i] - 1 for i in range(n)]

    # differ[(i, j)] is 1 when S_i and S_j have different signs, for i < j
    differ = {}
    for i in range(n):
        for j in range(i + 1, n):
            d = pulp.LpVariable(f"differ_{i}_{j}", cat="Binary")
            # differ is 1 exactly when the two bits are not equal
            problem += d >= bit[i] - bit[j]
            problem += d >= bit[j] - bit[i]
            problem += d <= bit[i] + bit[j]
            problem += d <= 2 - bit[i] - bit[j]
            differ[(i, j)] = d

    # the energy terms, one squared autocorrelation for each shift k
    energy_terms = []
    for k in range(1, n):
        # the pairs of positions i and (i + k) mod n, one for each i
        pairs = [differ[(min(i, (i + k) % n), max(i, (i + k) % n))] for i in range(n)]

        # the k-th periodic autocorrelation C_k, an integer between -n and n
        C = pulp.LpVariable(f"C_{k}", -n, n, cat="Integer")
        # each pair adds +1 when its signs agree and -1 when they differ
        problem += C == n - 2 * pulp.lpSum(pairs)

        # C_k squared. The square is convex, so it is enough to keep it above the tangent
        # line at every value C_k can take. C_k has the parity of n, so only those values count.
        square = pulp.LpVariable(f"square_{k}", 0, n * n)
        for v in range(-n, n + 1):
            if (v - n) % 2 == 0:
                problem += square >= 2 * v * C - v * v
        energy_terms.append(square)

    # the energy: the sum of the squared autocorrelations
    problem += pulp.lpSum(energy_terms)

    return problem, {"sequence": sequence}


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

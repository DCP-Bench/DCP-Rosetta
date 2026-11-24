# autoref: a CPLEX (Python) model from DCP Rosetta.
# Download the `autoref.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python autoref.py autoref.json

from docplex.mp.model import Model


def create_model(instance):
    """Autoref: find a series S = (s_0, s_1, ..., s_n, s_{n+1}) of integers between 0 and n such
    that each integer i from 0 to n occurs exactly s_i times in S, and the last term s_{n+1} is m."""
    n = instance["n"]  # the series has n + 2 terms, with values between 0 and n
    m = instance["m"]  # the value of the last term s_{n+1}

    model = Model("autoref")

    # S has n + 2 entries (indices 0..n+1) with values 0..n, and each value i occurs s_i times.
    # Counting the entries gives s_0 + ... + s_n = n + 2, and adding them up
    # gives 0*s_0 + 1*s_1 + ... + n*s_n = (s_0 + ... + s_n) + s_{n+1} = n + 2 + m. So the value
    # of s_j, for j >= 1, is at most (n + 2 + m) // j. This bound keeps the number of 0/1
    # variables small: a variable for every pair (index, value) would be (n + 1)^2, which is
    # more than the Community Edition's 1000 variables for n = 40.
    top = [n] + [min(n, (n + 2 + m) // j) for j in range(1, n + 1)]  # top[j]: the largest value s_j can take

    # holds[j][v] is 1 when s_j = v, for the indices j = 0..n and the values v = 0..top[j].
    holds = [[model.binary_var(name=f"holds_{j}_{v}") for v in range(top[j] + 1)]
             for j in range(n + 1)]

    # Each index j from 0 to n holds exactly one value.
    model.add_constraints(model.sum(holds[j]) == 1 for j in range(n + 1))

    # s[j] is the value held by index j; the last term s_{n+1} is m.
    s = [model.sum(v * holds[j][v] for v in range(top[j] + 1)) for j in range(n + 1)] + [m]

    # For each i from 0 to n, the number i occurs s_i times in the whole series: in the entries
    # 0..n that hold the value i, plus the last entry when m equals i.
    for i in range(n + 1):
        occurrences = model.sum(holds[j][i] for j in range(n + 1) if i <= top[j]) + (1 if m == i else 0)
        model.add_constraint(s[i] == occurrences)

    return model, {"s": s}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)

# csplib_076_costas_arrays: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

from docplex.mp.model import Model


def create_model(instance):
    """Costas array: a permutation costas of 1..n such that, for every distance d, the differences
    costas[j + d] - costas[j] over all positions j are all different (each row of the difference
    triangle holds different values)."""
    n = instance["n"]  # size of the Costas array

    positions = range(n)
    values = range(1, n + 1)

    model = Model("costas_array")
    # There is no objective, only a solution to find: tell CPLEX to favour finding one.
    model.parameters.emphasis.mip = 1

    # at[j, v] is 1 when position j holds the value v. The values are all different: each
    # position holds one value and each value is used once.
    at = {(j, v): model.binary_var(name=f"at_{j}_{v}") for j in positions for v in values}
    for j in positions:
        model.add_constraint(model.sum(at[j, v] for v in values) == 1)
    for v in values:
        model.add_constraint(model.sum(at[j, v] for j in positions) == 1)

    # costas[j] is the value at position j.
    costas = [model.sum(v * at[j, v] for v in values) for j in positions]

    # All entries in a row of the difference triangle are distinct. Row d - 1 holds the
    # differences costas[j + d] - costas[j]; the last row (distance n - 1) has a single entry
    # and needs no constraint. For each pair of entries of a row, larger is 1
    # when the second difference is the larger one. There are C(n, 3) such pairs, 220 at
    # n = 12, two indicator constraints each.
    for d in range(1, n - 1):
        diff = [costas[j + d] - costas[j] for j in range(n - d)]
        for a in range(n - d):
            for b in range(a + 1, n - d):
                larger = model.binary_var(name=f"larger_{d}_{a}_{b}")
                model.add_indicator(larger, diff[a] + 1 <= diff[b], active_value=1)
                model.add_indicator(larger, diff[b] + 1 <= diff[a], active_value=0)

    return model, {"costas": costas}


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

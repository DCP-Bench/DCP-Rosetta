# bales_of_hay: a CPLEX (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python bales_of_hay.py bales_of_hay.json

from docplex.mp.model import Model


def create_model(instance):
    """Bales of hay: recover the weight of each bale from the unlabelled weights of every pair of bales."""
    n = instance["n"]              # the number of bales
    weights = instance["weights"]  # the written-down pair weights, in no particular order
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]  # every combination of two bales
    written = range(len(weights))
    pair_ids = range(len(pairs))

    model = Model("bales_of_hay")

    # bales[i] is the weight of bale i: not negative, and at most the heaviest pair weight, since
    # every pair holding bale i also holds another bale of weight at least 0.
    bales = model.integer_var_list(n, 0, max(weights), name="bales")

    # matches[k, p] is 1 when written weight k is the weight of pair p.
    matches = model.binary_var_matrix(written, pair_ids, name="matches")

    # Every written weight belongs to exactly one pair, and no pair takes two
    # written weights: each weight was recorded for a pair of its own.
    model.add_constraints(model.sum(matches[k, p] for p in pair_ids) == 1 for k in written)
    model.add_constraints(model.sum(matches[k, p] for k in written) <= 1 for p in pair_ids)

    # A written weight matched to a pair is that pair's total weight.
    for k in written:
        for p, (i, j) in enumerate(pairs):
            model.add_indicator(matches[k, p], bales[i] + bales[j] == weights[k], name=f"weighs_{k}_{p}")

    return model, {"bales": bales}


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

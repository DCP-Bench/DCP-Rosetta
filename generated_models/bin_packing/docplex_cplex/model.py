# bin_packing: a CPLEX (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python bin_packing.py bin_packing.json

from docplex.mp.model import Model


def create_model(instance):
    """Bin packing: put every item in one of the bins so that no bin holds more than its capacity."""
    weights = instance["weights"]    # weights[j]: the weight of item j
    capacity = instance["capacity"]  # the most weight a bin can hold
    items = range(len(weights))
    bins = range(instance["num_bins"])  # the number of bins available

    model = Model("bin_packing")

    # put[j, b] is 1 when item j goes into bin b.
    put = model.binary_var_matrix(items, bins, name="put")

    # Every item goes into exactly one bin.
    model.add_constraints(model.sum(put[j, b] for b in bins) == 1 for j in items)

    # The items in a bin weigh no more than the bin's capacity.
    model.add_constraints(model.sum(weights[j] * put[j, b] for j in items) <= capacity for b in bins)

    # The bin of each item, 0-indexed, read back from the assignment.
    bin_of = [model.sum(b * put[j, b] for b in bins) for j in items]
    return model, {"bins": bin_of}


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

# four_numbers: a CPLEX (Python) model from DCP Rosetta.
# Download the `four_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python four_numbers.py four_numbers.json

from docplex.mp.model import Model


def create_model(instance):
    """Four numbers: find three integers in 1..10 from whose subset sums every given number can be made."""
    # The three numbers to find each lie in 1..10, as the problem states.
    LOW, HIGH = 1, 10
    PARTS = range(3)  # the three numbers to find
    numbers = instance["numbers"]  # the given numbers, each the sum of a subset of the three
    targets = range(len(numbers))

    model = Model("four_numbers")

    # x[j] is the j-th of the three numbers.
    x = model.integer_var_list(len(PARTS), LOW, HIGH, name="x")

    # uses[i, j] is 1 when x[j] is part of the subset that sums to numbers[i].
    uses = model.binary_var_matrix(targets, PARTS, name="uses")

    # part[i, j] is uses[i, j] * x[j]. CPLEX refuses a product of two variables
    # as non-convex, so it is written linearly: part is 0 when uses is 0, and
    # equals x[j] when uses is 1, using the bounds 1..10 of x.
    part = model.integer_var_matrix(targets, PARTS, 0, HIGH, name="part")
    for i in targets:
        for j in PARTS:
            model.add_constraint(part[i, j] <= HIGH * uses[i, j], ctname=f"off_high_{i}_{j}")
            model.add_constraint(part[i, j] >= LOW * uses[i, j], ctname=f"off_low_{i}_{j}")
            model.add_constraint(part[i, j] <= x[j] - LOW * (1 - uses[i, j]), ctname=f"on_high_{i}_{j}")
            model.add_constraint(part[i, j] >= x[j] - HIGH * (1 - uses[i, j]), ctname=f"on_low_{i}_{j}")

    # Each given number is the sum of its subset of the three.
    model.add_constraints(model.sum(part[i, j] for j in PARTS) == numbers[i] for i in targets)

    return model, {"x": x}


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

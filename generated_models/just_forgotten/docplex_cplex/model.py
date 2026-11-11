# just_forgotten: a CPLEX (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python just_forgotten.py just_forgotten.json

from docplex.mp.model import Model


def create_model(instance):
    """Just forgotten: recover an account number that uses each digit 0..n-1 once, knowing how many digits of each tried set were in place."""
    sets = instance["sets"]  # sets[k][i]: the digit at position i of the k-th number Joe tried
    correct = instance["num_correct_digits"]  # in each tried number, this many digits are in their correct position
    n = len(sets[0])  # the number of digits of the account number
    positions = range(n)
    digits = range(n)

    model = Model("just_forgotten")

    # digit_at[i, d] is 1 when position i of the account number holds digit d.
    digit_at = model.binary_var_matrix(positions, digits, name="digit_at")

    # Every position holds one digit, and every digit 0..n-1 is used once.
    model.add_constraints(model.sum(digit_at[i, d] for d in digits) == 1 for i in positions)
    model.add_constraints(model.sum(digit_at[i, d] for i in positions) == 1 for d in digits)

    # In each tried set, exactly the given number of digits are in their correct position.
    model.add_constraints(model.sum(digit_at[i, tried[i]] for i in positions if tried[i] in digits) == correct
                          for tried in sets)

    # x[i] is the digit at position i of the account number.
    x = [model.sum(d * digit_at[i, d] for d in digits) for i in positions]
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

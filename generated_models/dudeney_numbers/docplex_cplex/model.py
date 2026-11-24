# dudeney_numbers: a CPLEX (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python dudeney_numbers.py dudeney_numbers.json

from docplex.mp.model import Model


def create_model(instance):
    """Dudeney numbers: find a number larger than 1 with at most n digits that is a perfect cube whose
    cube root equals the sum of its digits."""
    n = instance["n"]  # maximum number of digits
    top = 10 ** n - 1  # largest number with n digits

    model = Model("dudeney_numbers")

    # digit[i] is the i-th digit of the number, most significant first.
    digit = [model.integer_var(0, 9, name=f"digit_{i}") for i in range(n)]
    number = model.integer_var(0, top, name="number")

    # The number is written by its digits.
    model.add_constraint(number == model.sum(digit[i] * 10 ** (n - i - 1) for i in range(n)))

    # The cube root is the digit sum, so it lies in 1..9n (n digits of at most 9 each).
    # number = root^3 multiplies variables, which CPLEX refuses, so the root is chosen one-hot
    # among the values whose cube still has at most n digits.
    roots = [r for r in range(1, 9 * n + 1) if r ** 3 <= top]
    is_root = {r: model.binary_var(name=f"is_root_{r}") for r in roots}
    model.add_constraint(model.sum(is_root.values()) == 1)
    cube_root = model.sum(r * is_root[r] for r in roots)

    # The number is the cube of its cube root.
    model.add_constraint(number == model.sum(r ** 3 * is_root[r] for r in roots))

    # The cube root equals the sum of the digits.
    model.add_constraint(cube_root == model.sum(digit))

    # The number is larger than 1.
    model.add_constraint(number >= 2)

    return model, {"number": number}


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

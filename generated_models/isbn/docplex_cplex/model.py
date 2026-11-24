# isbn: a CPLEX (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python isbn.py isbn.json

from docplex.mp.model import Model


def create_model(instance):
    """ISBN-13: fill in the unknown digits so that the number starts with 978 or 979 and its check digit is right."""
    known = instance["isbn_init"]  # known[i]: the i-th digit, or -1 where it is unknown
    length = 13  # an ISBN-13 has 13 digits
    n_weighted = length - 1  # the first 12 digits are weighted; the last one is the check digit
    weights = [1 if i % 2 == 0 else 3 for i in range(n_weighted)]  # alternately 1 and 3, starting with 1

    model = Model("isbn")

    # isbn[i] is the i-th digit.
    isbn = model.integer_var_list(length, 0, 9, name="isbn")

    # The known digits keep their values.
    model.add_constraints(isbn[i] == known[i] for i in range(length) if known[i] != -1)

    # The number starts with 978 or 979.
    model.add_constraint(isbn[0] == 9, ctname="prefix0")
    model.add_constraint(isbn[1] == 7, ctname="prefix1")
    model.add_constraint(isbn[2] >= 8, ctname="prefix2")

    # The check digit is (10 - (sum % 10)) % 10 of the weighted sum of the first
    # 12 digits. Because it is a single digit, that is the same as saying the
    # weighted sum plus the check digit is a multiple of 10, which is linear.
    # tens is that multiple of 10 divided by 10; its upper bound is the largest possible sum
    # (every digit 9), so it cannot cut off a solution.
    tens = model.integer_var(0, (9 * sum(weights) + 9) // 10, name="tens")
    model.add_constraint(model.scal_prod(isbn[:n_weighted], weights) + isbn[-1] == 10 * tens)

    return model, {"isbn": isbn}


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

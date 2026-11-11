# session1_bank_card: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python session1_bank_card.py

from docplex.mp.model import Model


def create_model(instance):
    """A bank card has a 4 digit PIN abcd: no two digits are the same, the 2-digit number cd is
    3 times the 2-digit number ab, and the 2-digit number da is 2 times the 2-digit number bc."""
    letters = "abcd"  # the four digits of the PIN, in order
    digits = range(10)  # a PIN digit is 0 to 9

    model = Model("bank_card")

    # is_digit[c, v] is 1 when PIN digit c is v
    is_digit = {(c, v): model.binary_var(name=f"{c}_is_{v}") for c in letters for v in digits}

    # Each PIN digit has exactly one value.
    model.add_constraints(model.sum(is_digit[c, v] for v in digits) == 1 for c in letters)

    # No two digits are the same.
    model.add_constraints(model.sum(is_digit[c, v] for c in letters) <= 1 for v in digits)

    # value[c] is the value of PIN digit c
    value = {c: model.sum(v * is_digit[c, v] for v in digits) for c in letters}
    a, b, c, d = (value[x] for x in letters)

    # The two-digit number cd is 3 times the two-digit number ab.
    model.add_constraint(10 * c + d == 3 * (10 * a + b))
    # The two-digit number da is 2 times the two-digit number bc.
    model.add_constraint(10 * d + a == 2 * (10 * b + c))

    return model, dict(value)


if __name__ == "__main__":
    model, outputs = create_model({})
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

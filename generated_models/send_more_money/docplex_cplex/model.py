# send_more_money: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python send_more_money.py

from docplex.mp.model import Model


def create_model(instance):
    """SEND + MORE = MONEY: each letter stands for a different digit from 0 to 9 so that the sum
    holds, and the first letter of each word is not zero."""
    letters = "sendmory"  # the eight different letters
    digits = range(10)    # the digits 0 to 9

    model = Model("send_more_money")

    # is_digit[c, d] is 1 when letter c stands for digit d
    is_digit = {(c, d): model.binary_var(name=f"{c}_is_{d}") for c in letters for d in digits}

    # Each letter stands for exactly one digit.
    model.add_constraints(model.sum(is_digit[c, d] for d in digits) == 1 for c in letters)

    # Different letters stand for different digits.
    model.add_constraints(model.sum(is_digit[c, d] for c in letters) <= 1 for d in digits)

    # value[c] is the digit that letter c stands for
    value = {c: model.sum(d * is_digit[c, d] for d in digits) for c in letters}
    s, e, n, d, m, o, r, y = (value[c] for c in letters)

    # SEND + MORE = MONEY.
    model.add_constraint(1000 * s + 100 * e + 10 * n + d
                         + 1000 * m + 100 * o + 10 * r + e
                         == 10000 * m + 1000 * o + 100 * n + 10 * e + y)
    # S and M lead their words, so they are not zero.
    model.add_constraint(s >= 1)
    model.add_constraint(m >= 1)

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

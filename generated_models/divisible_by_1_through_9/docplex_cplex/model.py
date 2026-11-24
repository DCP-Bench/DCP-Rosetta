# divisible_by_1_through_9: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python divisible_by_1_through_9.py

from docplex.mp.model import Model


def create_model(instance):
    """Divisible by 1 through 10: find a ten-digit number using each digit 0..9 once, such that
    the number formed by its first n digits is divisible by n, for n = 1..10."""
    n = 10  # the number has 10 digits; its first k digits must be divisible by k
    positions = range(n)
    digits = range(n)  # the digits 0..9, each used exactly once

    model = Model("divisible_by_1_through_9")

    # is_digit[i, d] is 1 when position i (from the left) holds digit d. Each position holds
    # one digit and every digit is used exactly once.
    is_digit = {(i, d): model.binary_var(name=f"pos_{i}_is_{d}") for i in positions
                for d in digits}
    for i in positions:
        model.add_constraint(model.sum(is_digit[i, d] for d in digits) == 1)
    for d in digits:
        model.add_constraint(model.sum(is_digit[i, d] for i in positions) == 1)

    def digit(i):
        return model.sum(d * is_digit[i, d] for d in digits)

    # The number formed by the first k digits is divisible by k. That prefix is
    # sum_j digit_j * 10^(k-1-j); modulo k each power of ten can be replaced by its remainder,
    # which keeps the coefficients below k instead of up to 10^9 (CPLEX works in doubles).
    # The reduced sum is then a multiple of k: it equals k * q for an integer q >= 0.
    for k in range(1, n + 1):
        coefficients = [pow(10, k - 1 - j, k) for j in range(k)]
        reduced = model.sum(c * digit(j) for j, c in enumerate(coefficients) if c)
        top = sum(9 * c for c in coefficients) // k  # the reduced sum is at most 9 * sum(c)
        q = model.integer_var(0, top, name=f"quotient_{k}")
        model.add_constraint(reduced == k * q)

    # The digits of the number, read from left to right.
    return model, {"digits": [digit(i) for i in positions]}


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

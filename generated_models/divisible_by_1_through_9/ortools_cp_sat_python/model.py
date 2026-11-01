# divisible_by_1_through_9: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install ortools`) with:
#   python divisible_by_1_through_9.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Find a ten-digit number that uses each of the digits 0 to 9 exactly once,
    where the number formed by its first n digits is divisible by n, for every n
    from 1 to 10."""
    n_digits = 10  # the number of digits in the number

    model = cp_model.CpModel()

    # digits[i] is the i-th digit of the number, read from left to right
    digits = [model.new_int_var(0, 9, f"digits_{i}") for i in range(n_digits)]
    # prefix[i] is the number formed by the first i + 1 digits
    prefix = [model.new_int_var(0, 10**n_digits, f"prefix_{i}") for i in range(n_digits)]
    # number is the whole ten-digit number
    number = prefix[n_digits - 1]

    # Each digit from 0 to 9 is used exactly once.
    model.add_all_different(digits)
    for i in range(n_digits):
        # The leftmost digit has the highest place value.
        model.add(prefix[i] == sum(digits[j] * 10 ** (i - j) for j in range(i + 1)))
        # The number formed by the first i + 1 digits is divisible by i + 1.
        # remainder is the remainder of that number after division by i + 1.
        remainder = model.new_int_var(0, i, f"remainder_{i}")
        model.add_modulo_equality(remainder, prefix[i], i + 1)
        model.add(remainder == 0)

    return model, {"number": number}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

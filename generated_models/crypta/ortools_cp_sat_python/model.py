# crypta: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install ortools`) with:
#   python crypta.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Cryptarithmetic puzzle: each of the letters A to J stands for a different digit
    from 0 to 9, no number starts with a zero, and the addition of the two twenty-letter
    numbers must give the third."""

    def number(digits):
        """The number written by a list of digits, most significant digit first."""
        return sum(digit * 10 ** k for k, digit in enumerate(reversed(digits)))

    model = cp_model.CpModel()

    # The digit of each letter A to J. The first letters B, D and G of the three numbers are not zero.
    letters = [model.new_int_var(1 if name in "BDG" else 0, 9, name) for name in "ABCDEFGHIJ"]
    A, B, C, D, E, F, G, H, I, J = letters
    # carry1 is 1 when the lowest seven digits carry into the middle seven digits, and
    # carry2 is 1 when the middle seven digits carry into the top six digits
    carry1 = model.new_int_var(0, 1, "carry1")
    carry2 = model.new_int_var(0, 1, "carry2")

    # All letters stand for different digits.
    model.add_all_different(letters)

    # The lowest seven digits of the two numbers add up to the lowest seven digits of the
    # result, plus the carry into the middle block.
    model.add(number([F, E, B, B, J, E, A]) + number([F, A, G, F, E, J, E])
              == number([B, F, I, H, E, E, F]) + 10 ** 7 * carry1)
    # The middle seven digits, plus the carry from the lowest block, add up to the middle
    # seven digits of the result, plus the carry into the top block.
    model.add(number([J, I, I, A, H, F, C]) + number([C, D, I, D, B, I, F]) + carry1
              == number([D, D, H, F, A, F, J]) + 10 ** 7 * carry2)
    # The top six digits, plus the carry from the middle block, give the top six digits of
    # the result with no carry out.
    model.add(number([B, A, I, J, J, A]) + number([D, H, F, G, A, B]) + carry2
              == number([G, J, E, G, A, C]))

    return model, {"A": A, "B": B, "C": C, "D": D, "E": E,
                   "F": F, "G": G, "H": H, "I": I, "J": J}


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

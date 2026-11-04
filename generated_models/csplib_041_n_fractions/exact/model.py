# csplib_041_n_fractions: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install exact numpy`) with:
#   python csplib_041_n_fractions.py

from exact import Exact


def create_model(instance):
    """Find distinct non-zero digits A to I such that A / BC + D / EF + G / HI = 1, where BC, EF
    and HI are the two-digit numbers formed by B and C, E and F, and H and I."""
    solver = Exact()

    # The nine letters of the puzzle.
    letters = list("ABCDEFGHI")

    # Exact identifies its variables by name.
    # A new variable equal to the product of its factors.
    def product(name, factors, low, high):
        solver.addVariable(name, low, high)
        solver.addMultiplication(factors, True, name, True, name)

    # Each letter is a digit from 1 to 9.
    for name in letters:
        solver.addVariable(name, 1, 9)

    # digit_is[name][d] is 1 when the letter name stands for the digit d.
    digit_is = {name: {d: f"{name}_is_{d}" for d in range(1, 10)} for name in letters}
    for name in letters:
        for d in range(1, 10):
            solver.addVariable(digit_is[name][d], 0, 1)
        # Each letter stands for exactly one digit.
        solver.addConstraint([(1, digit_is[name][d]) for d in range(1, 10)], True, 1, True, 1)
        # The letter is the digit it stands for.
        solver.addConstraint([(d, digit_is[name][d]) for d in range(1, 10)] + [(-1, name)], True, 0, True, 0)

    # The nine letters are nine different digits: each digit is used by exactly one letter.
    for d in range(1, 10):
        solver.addConstraint([(1, digit_is[name][d]) for name in letters], True, 1, True, 1)

    # D1, D2 and D3 stand for the two-digit numbers BC, EF and HI: ten times the tens digit plus the units digit.
    for number, tens, units in (("D1", "B", "C"), ("D2", "E", "F"), ("D3", "H", "I")):
        solver.addVariable(number, 11, 99)
        solver.addConstraint([(1, number), (-10, tens), (-1, units)], True, 0, True, 0)

    # Multiply the equation by D1 * D2 * D3 to clear the fractions.
    product("D1D2", ["D1", "D2"], 11 * 11, 99 * 99)
    product("D1D3", ["D1", "D3"], 11 * 11, 99 * 99)
    product("D2D3", ["D2", "D3"], 11 * 11, 99 * 99)
    product("D1D2D3", ["D1D2", "D3"], 11 * 11 * 11, 99 * 99 * 99)
    product("A_D2D3", ["A", "D2D3"], 1 * 11 * 11, 9 * 99 * 99)
    product("D_D1D3", ["D", "D1D3"], 1 * 11 * 11, 9 * 99 * 99)
    product("G_D1D2", ["G", "D1D2"], 1 * 11 * 11, 9 * 99 * 99)

    # A * D2 * D3 + D * D1 * D3 + G * D1 * D2 equals D1 * D2 * D3.
    solver.addConstraint([(1, "A_D2D3"), (1, "D_D1D3"), (1, "G_D1D2"), (-1, "D1D2D3")], True, 0, True, 0)

    return solver, {name: name for name in letters}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

# crypta: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install cpmpy`) with:
#   python crypta.py

import cpmpy as cp


def number(digits):
    """The number written by a list of digits, most significant digit first."""
    return cp.sum([digit * 10 ** k for k, digit in enumerate(reversed(digits))])


def create_model(instance):
    """Cryptarithmetic puzzle: each of the letters A to J stands for a different
    digit from 0 to 9, no number starts with a zero, and the addition of the two
    twenty-letter numbers must give the third. The puzzle fixes all its data."""
    # letters[0..9] are the digits of the letters A..J
    letters = cp.intvar(0, 9, shape=10, name="letters")
    A, B, C, D, E, F, G, H, I, J = letters

    # The twenty-letter addition is checked in blocks of seven digits, from the right.
    # carry1 is what the lowest block carries into the middle block, carry2 what the
    # middle block carries into the top block.
    carry1 = cp.intvar(0, 1, name="carry1")
    carry2 = cp.intvar(0, 1, name="carry2")

    model = cp.Model()

    # All letters stand for different digits.
    model.add(cp.AllDifferent(letters))

    # The first letter of each number is not zero (B, D and G start the three numbers).
    model.add([B >= 1, D >= 1, G >= 1])

    # Lowest block: the last seven digits of the two numbers add up to the last seven
    # digits of the result, plus the carry into the next block.
    model.add(number([F, E, B, B, J, E, A]) + number([F, A, G, F, E, J, E])
              == number([B, F, I, H, E, E, F]) + 10 ** 7 * carry1)
    # Middle block: the next seven digits, plus the incoming carry.
    model.add(number([J, I, I, A, H, F, C]) + number([C, D, I, D, B, I, F]) + carry1
              == number([D, D, H, F, A, F, J]) + 10 ** 7 * carry2)
    # Top block: the first six digits, plus the incoming carry, with no carry out.
    model.add(number([B, A, I, J, J, A]) + number([D, H, F, G, A, B]) + carry2
              == number([G, J, E, G, A, C]))

    return model, {"A": A, "B": B, "C": C, "D": D, "E": E,
                   "F": F, "G": G, "H": H, "I": I, "J": J}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

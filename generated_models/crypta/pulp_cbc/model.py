# crypta: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install pulp numpy`) with:
#   python crypta.py

import pulp


def create_model(instance):
    """Cryptarithmetic puzzle: each of the letters A to J stands for a different
    digit from 0 to 9, no number starts with a zero, and the addition of the two
    twenty-letter numbers must give the third."""

    def number(digits):
        """The number written by a list of digits, most significant digit first."""
        return pulp.lpSum(value * 10 ** k for k, value in enumerate(reversed(digits)))

    names = "ABCDEFGHIJ"
    problem = pulp.LpProblem("crypta", pulp.LpMinimize)

    # digit[name] is the digit that the letter stands for. B, D and G start the three numbers, so they are not zero.
    digit = {name: pulp.LpVariable(name, 1 if name in "BDG" else 0, 9, cat="Integer")
             for name in names}

    # pick[name][d] is 1 when the letter stands for the digit d.
    pick = {name: {d: pulp.LpVariable(f"pick_{name}_{d}", cat="Binary") for d in range(10)}
            for name in names}
    for name in names:
        # Each letter stands for exactly one digit.
        problem += pulp.lpSum(pick[name].values()) == 1
        # The digit of the letter is the digit it picks.
        problem += digit[name] == pulp.lpSum(d * pick[name][d] for d in range(10))
    # Different letters stand for different digits: each digit is taken by exactly one letter.
    for d in range(10):
        problem += pulp.lpSum(pick[name][d] for name in names) == 1

    A, B, C, D, E, F, G, H, I, J = (digit[name] for name in names)

    # carry1 is 1 when the lowest seven digits carry into the middle seven digits, and
    # carry2 is 1 when the middle seven digits carry into the top six digits.
    carry1 = pulp.LpVariable("carry1", cat="Binary")
    carry2 = pulp.LpVariable("carry2", cat="Binary")

    # The lowest seven digits of the two added numbers, plus nothing, give the lowest
    # seven digits of the sum, with carry1 going into the middle block.
    problem += (number([F, E, B, B, J, E, A]) + number([F, A, G, F, E, J, E])
                == number([B, F, I, H, E, E, F]) + 10 ** 7 * carry1)
    # The middle seven digits of the two added numbers, plus carry1, give the middle seven
    # digits of the sum, with carry2 going into the top block.
    problem += (number([J, I, I, A, H, F, C]) + number([C, D, I, D, B, I, F]) + carry1
                == number([D, D, H, F, A, F, J]) + 10 ** 7 * carry2)
    # The top six digits of the two added numbers, plus carry2, give the top six digits
    # of the sum, with nothing carried out.
    problem += (number([B, A, I, J, J, A]) + number([D, H, F, G, A, B]) + carry2
                == number([G, J, E, G, A, C]))

    return problem, {name: digit[name] for name in names}


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

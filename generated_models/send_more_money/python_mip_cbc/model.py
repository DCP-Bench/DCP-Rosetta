# send_more_money: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install mip numpy`) with:
#   python send_more_money.py

import mip


def create_model(instance):
    """Cryptarithmetic puzzle: give each letter a different digit so that
    SEND + MORE = MONEY holds, with no leading zero in any word."""
    letters = ["s", "e", "n", "d", "m", "o", "r", "y"]  # the letters of the puzzle

    model = mip.Model(solver_name="CBC")

    # digit[letter]: the digit the letter stands for. The first letters of SEND and MORE are not 0.
    digit = {}
    for letter in letters:
        lb = 1 if letter in ("s", "m") else 0
        digit[letter] = model.add_var(letter, lb=lb, ub=9, var_type=mip.INTEGER)

    # choice[letter][v] is 1 when the letter stands for digit v (v from 0 to 9), and 0 when not
    choice = {}
    for letter in letters:
        choice[letter] = [model.add_var(f"c_{letter}_{v}", var_type=mip.BINARY) for v in range(10)]
        # Each letter stands for exactly one digit.
        model += mip.xsum(choice[letter]) == 1
        # The digit of the letter is the digit it is chosen for.
        model += digit[letter] == mip.xsum(v * choice[letter][v] for v in range(10))

    # Different letters stand for different digits: each digit goes to at most one letter.
    for v in range(10):
        model += mip.xsum(choice[letter][v] for letter in letters) <= 1

    # SEND + MORE - MONEY = 0, with the coefficients of each letter added up over the three words.
    # For example, e is worth 100 in SEND, 1 in MORE and -10 in MONEY, which gives 91.
    model += mip.xsum([
        1000 * digit["s"],
        91 * digit["e"],
        -90 * digit["n"],
        1 * digit["d"],
        -9000 * digit["m"],
        -900 * digit["o"],
        10 * digit["r"],
        -1 * digit["y"],
    ]) == 0

    return model, {letter: digit[letter] for letter in letters}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

# send_more_money: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install pulp numpy`) with:
#   python send_more_money.py

import pulp


def create_model(instance):
    """SEND + MORE = MONEY: give each letter a different digit so that the sum holds, with no
    word starting with zero."""
    letters = ["s", "e", "n", "d", "m", "o", "r", "y"]  # the letters of the puzzle
    digits = range(10)                                  # the digits 0 to 9

    problem = pulp.LpProblem("send_more_money", pulp.LpMinimize)

    # is_digit[ch][v] is 1 when letter ch stands for digit v, and 0 otherwise
    is_digit = {ch: [pulp.LpVariable(f"is_{ch}_{v}", cat="Binary") for v in digits]
                for ch in letters}
    # value[ch]: the digit that letter ch stands for
    value = {ch: pulp.lpSum(v * is_digit[ch][v] for v in digits) for ch in letters}

    # number(word): the decimal number that a word spells with the digits of its letters
    def number(word):
        return pulp.lpSum(10 ** (len(word) - 1 - k) * value[ch] for k, ch in enumerate(word))

    # Each letter stands for exactly one digit.
    for ch in letters:
        problem += pulp.lpSum(is_digit[ch]) == 1

    # Each digit is used by at most one letter.
    for v in digits:
        problem += pulp.lpSum(is_digit[ch][v] for ch in letters) <= 1

    # The first letters of SEND and MORE are not zero.
    problem += is_digit["s"][0] == 0
    problem += is_digit["m"][0] == 0

    # SEND + MORE = MONEY
    problem += number("send") + number("more") == number("money")

    return problem, value


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

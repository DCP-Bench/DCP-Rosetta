# general_store: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install pulp numpy`) with:
#   python general_store.py

import pulp


def create_model(instance):
    """The owner of a general store has put up a sign: sixteen words that add up to
    'ALL WOOL'. Each different letter stands for a different digit; find the digit
    of every letter. The sign fixes all the data, so the instance is not used."""
    # The letters on the sign, each standing for one digit.
    letters = ["C", "H", "E", "S", "A", "B", "O", "W", "P", "L"]
    # The sixteen words above the line.
    words = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
             "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
    # The total below the line.
    total = "ALLWOOL"
    digits = range(10)

    problem = pulp.LpProblem("general_store", pulp.LpMinimize)

    # is_digit[ch][v] is 1 when the letter ch stands for the digit v, and 0 when not.
    is_digit = {ch: [pulp.LpVariable(f"is_{ch}_{v}", cat="Binary") for v in digits]
                for ch in letters}
    # The digit each letter stands for.
    value = {ch: pulp.lpSum(v * is_digit[ch][v] for v in digits) for ch in letters}

    # The number a word spells, its last letter in the units place.
    def number(word):
        return pulp.lpSum(10 ** (len(word) - 1 - k) * value[ch] for k, ch in enumerate(word))

    # Each letter stands for exactly one digit.
    for ch in letters:
        problem += pulp.lpSum(is_digit[ch]) == 1

    # Different letters stand for different digits.
    for v in digits:
        problem += pulp.lpSum(is_digit[ch][v] for ch in letters) <= 1

    # The sixteen words above the line add up to the total.
    problem += pulp.lpSum(number(word) for word in words) == number(total)

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

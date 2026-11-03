# general_store: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install mip numpy`) with:
#   python general_store.py

import mip

# The sixteen words above the line.
WORDS = [
    "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
    "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP",
]
# The total below the line.
TOTAL = "ALLWOOL"
# The letters of the puzzle.
LETTERS = ["A", "B", "C", "E", "H", "L", "O", "P", "S", "W"]


def create_model(instance):
    """The owner of a general store has put up a sign with sixteen words that add up
    to 'ALL WOOL'. Each different letter stands for a different digit. Find the digit
    of every letter."""
    model = mip.Model(solver_name="CBC")
    # The ten digits.
    digits = range(10)

    # p[L][d] is 1 when letter L stands for digit d, and 0 when not.
    p = {L: {d: model.add_var(name=f"p_{L}_{d}", var_type=mip.BINARY) for d in digits}
         for L in LETTERS}
    # x[L] is the digit that letter L stands for.
    x = {L: mip.xsum(d * p[L][d] for d in digits) for L in LETTERS}

    # Each letter stands for exactly one digit.
    for L in LETTERS:
        model.add_constr(mip.xsum(p[L][d] for d in digits) == 1)

    # Different letters stand for different digits.
    for d in digits:
        model.add_constr(mip.xsum(p[L][d] for L in LETTERS) <= 1)

    # Number of columns, the length of the longest word.
    width = max(len(w) for w in WORDS + [TOTAL])
    # carry[k] is what column k carries into the column to its left. A column holds
    # sixteen digits of at most 9 and a carry of at most 15, so its carry is at most 15.
    # The total has no digit beyond its last column, so the carry out of that column is 0.
    carry = [model.add_var(name=f"carry_{k}", lb=0, ub=0 if k == width - 1 else 15,
                           var_type=mip.INTEGER)
             for k in range(width)]

    # The sixteen words add up to 'ALL WOOL', column by column from the units place.
    for k in range(width):
        # coef[ch] is how many times letter ch appears in column k of the words, minus
        # one when it appears in the total in that column.
        coef = {}
        for word in WORDS:
            if k < len(word):
                ch = word[len(word) - 1 - k]
                coef[ch] = coef.get(ch, 0) + 1
        ch_total = TOTAL[len(TOTAL) - 1 - k]
        coef[ch_total] = coef.get(ch_total, 0) - 1
        # The column's terms, which sum to zero.
        terms = [c * x[L] for L, c in coef.items() if c != 0]
        if k > 0:
            terms.append(carry[k - 1])
        terms.append(-10 * carry[k])
        model.add_constr(mip.xsum(terms) == 0)

    outputs = {L: x[L] for L in LETTERS}
    return model, outputs


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

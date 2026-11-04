# crypta: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Run it (after `pip install mip numpy`) with:
#   python crypta.py

import mip


def create_model(instance):
    """Cryptarithmetic puzzle: each letter A to J stands for a different digit from 0 to 9,
    and the first letter of each number is not zero. The sum of the two twenty-letter
    addends must give the twenty-letter result."""
    # The two addends and their sum, written as letters.
    addend1 = "BAIJJAJIIAHFCFEBBJEA"
    addend2 = "DHFGABCDIDBIFFAGFEJE"
    result = "GJEGACDDHFAFJBFIHEEF"
    letters = "ABCDEFGHIJ"
    leading = {addend1[0], addend2[0], result[0]}
    n = len(result)

    model = mip.Model(solver_name="CBC")

    # The digits a letter may stand for: a leading letter is not zero.
    allowed = {L: range(1, 10) if L in leading else range(10) for L in letters}

    # digit[L] is the digit that letter L stands for.
    digit = {L: model.add_var(f"digit_{L}", lb=0, ub=9, var_type=mip.INTEGER) for L in letters}

    # choice[L, d] is 1 when letter L stands for digit d.
    choice = {(L, d): model.add_var(f"choice_{L}_{d}", var_type=mip.BINARY)
              for L in letters for d in allowed[L]}

    # Each letter stands for exactly one of its digits, and digit[L] is that digit.
    for L in letters:
        model += mip.xsum(choice[L, d] for d in allowed[L]) == 1
        model += digit[L] == mip.xsum(d * choice[L, d] for d in allowed[L])

    # Different letters stand for different digits.
    for d in range(10):
        model += mip.xsum(choice[L, d] for L in letters if (L, d) in choice) <= 1

    # carry[k] is the carry into column k, counting columns from the right. Nothing comes in
    # from the right, and nothing goes out past the leftmost column, since the sum has as
    # many digits as the addends.
    carry = [model.add_var(f"carry_{k}", lb=0, ub=0 if k in (0, n) else 1, var_type=mip.INTEGER)
             for k in range(n + 1)]

    # Column by column from the right, the addend digits plus the carry in equal the result
    # digit plus ten times the carry out.
    for k in range(n):
        # Net count of each letter in column k: +1 for an addend, -1 for the result.
        coef = {}
        for word, sign in ((addend1, 1), (addend2, 1), (result, -1)):
            L = word[len(word) - 1 - k]
            coef[L] = coef.get(L, 0) + sign
        model += mip.xsum(c * digit[L] for L, c in coef.items()) + carry[k] - 10 * carry[k + 1] == 0

    return model, {L: digit[L] for L in letters}


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

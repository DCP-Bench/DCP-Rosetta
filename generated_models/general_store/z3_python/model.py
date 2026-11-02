# general_store: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install z3-solver numpy`) with:
#   python general_store.py

import z3


def create_model(instance):
    """The owner of a general store has put up a sign: sixteen words that add up to
    'ALL WOOL'. Each different letter stands for a different digit; find the digit
    of every letter. The sign fixes all the data, so the instance is not used."""
    # The sixteen words above the line, and the total below it.
    words = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL",
             "BASS", "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP",
             "SHEEP"]
    total = "ALLWOOL"

    # The letters on the sign.
    letters = "CHESABOWPL"
    # digit[ch] is the digit that letter ch stands for, held in four bits.
    digit = {ch: z3.BitVec(ch, 4) for ch in letters}

    solver = z3.Solver()

    # Each letter stands for a digit from 0 to 9.
    solver.add([z3.ULE(digit[ch], 9) for ch in letters])
    # Different letters stand for different digits.
    solver.add(z3.Distinct([digit[ch] for ch in letters]))

    def wide(bv):
        # Widened to eight bits, so that sixteen digits and a carry cannot overflow.
        return z3.ZeroExt(4, bv)

    # carry[k] is the amount carried into the k-th column, counting from the units.
    width = len(total)
    carry = [z3.BitVec(f"carry_{k}", 4) for k in range(width + 1)]
    # Nothing is carried into the units column or out of the leftmost one.
    solver.add(carry[0] == 0, carry[width] == 0)

    # Column by column, the digits of the words and the carry add up to the digit of
    # the total plus ten times the carry out of the column.
    for k in range(width):
        column = [digit[w[len(w) - 1 - k]] for w in words if k < len(w)]
        column_sum = z3.Sum([wide(d) for d in column]) + wide(carry[k])
        written = wide(digit[total[width - 1 - k]]) + 10 * wide(carry[k + 1])
        solver.add(column_sum == written)

    # The digit of each letter.
    return solver, {ch: z3.BV2Int(digit[ch]) for ch in letters}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

# general_store: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install cvc5 numpy`) with:
#   python general_store.py

import cvc5.pythonic as c5


def create_model(instance):
    """A store owner's sign shows sixteen words above a line, which add up to ALL WOOL.
    Each different letter stands for a different digit. Find the digit of each letter."""
    # The ten letters, each standing for one digit.
    names = ["C", "H", "E", "S", "A", "B", "O", "W", "P", "L"]

    # Digits are kept in 8 bits: a column sum is at most 16 * 9 + 15 = 159.
    width = 8
    # letter[n] is the digit that letter n stands for.
    letter = {n: c5.BitVec(n, width) for n in names}

    # Arithmetic on the digits is done bit by bit: cvc5 then proves there is no second
    # solution in seconds, which it cannot do within the time limit with the default Solver().
    solver = c5.SolverFor("ALL")
    solver.set("bv-solver", "bitblast-internal")

    # Each letter stands for a digit from 0 to 9.
    solver.add(*[c5.ULE(letter[n], 9) for n in names])

    # Different letters stand for different digits.
    solver.add(c5.Distinct(*[letter[n] for n in names]))

    # The sixteen words above the line, and the total below it.
    words = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
             "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
    total = "ALLWOOL"

    # The words add up to the total column by column, from the units digit. In each
    # column, the digits of the words plus the carry from the column before equal the
    # digit of the total plus ten times the carry into the next column.
    carry_in = c5.BitVecVal(0, width)  # the carry into the units column is zero
    for k in range(len(total)):
        column = carry_in  # the sum of this column
        for w in words:
            if len(w) > k:
                column = column + letter[w[-1 - k]]
        if k + 1 < len(total):
            carry_out = c5.BitVec(f"carry_{k + 1}", width)
            # A carry is at most 15.
            solver.add(c5.ULE(carry_out, 15))
        else:
            # The leading column has no carry out.
            carry_out = c5.BitVecVal(0, width)
        solver.add(column == letter[total[-1 - k]] + 10 * carry_out)
        carry_in = carry_out

    # The digit of each letter, as a whole number.
    outputs = {n: c5.BV2Int(letter[n]) for n in names}
    return solver, outputs


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

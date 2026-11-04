# general_store: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/general_store.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python general_store.py

from collections import Counter
from functools import reduce
from operator import add

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """The owner of a general store has put up a sign: sixteen words that add up to
    'ALL WOOL'. Each different letter stands for a different digit; find the digit
    of every letter."""
    # The words above the line, and the total they add up to.
    words = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
             "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
    total = "ALLWOOL"
    # The letters on the sign, each once.
    letters = sorted(set("".join(words) + total))
    # The sum has one column for each letter of the total.
    n_columns = len(total)

    pool = IDPool()
    # digit[letter] is the digit that the letter stands for.
    digit = {letter: Integer(letter, 0, 9, vpool=pool) for letter in letters}
    # carry[k] is what column k passes on to column k + 1. A column adds sixteen digits,
    # so the carry is at most 15.
    carry = [Integer(f"carry_{k}", 0, 15, vpool=pool) for k in range(n_columns - 1)]
    engine = IntegerEngine(vars=list(digit.values()) + carry, vpool=pool)

    # Different letters stand for different digits.
    engine.add_alldifferent(list(digit.values()))

    # The columns add up, from the units column on the right.
    for k in range(n_columns):
        # net[letter]: how many words have the letter in column k, less one if the total
        # has it there.
        net = Counter(word[-1 - k] for word in words if len(word) > k)
        net[total[-1 - k]] -= 1
        # left holds the digits added in column k and the carry in; right holds the digits
        # taken away, and ten times the carry out.
        left = [count * digit[letter] for letter, count in net.items() if count > 0]
        right = [-count * digit[letter] for letter, count in net.items() if count < 0]
        # The first column takes no carry in, and the last gives none out.
        if k > 0:
            left.append(carry[k - 1])
        if k < n_columns - 1:
            right.append(10 * carry[k])
        engine.add_linear(reduce(add, left) == reduce(add, right))

    return engine.clausify(), {letter: digit[letter] for letter in letters}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

# building_blocks: a PySAT (Python) model from DCP Rosetta.
# Download the `building_blocks.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python building_blocks.py building_blocks.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Alphabet blocks carry one letter on each side, and together carry every letter used.
    Arranged in various ways they must spell every word of a given list; find which letters
    sit on which block."""
    num_blocks = instance["num_blocks"]    # the number of blocks
    num_sides = instance["num_sides"]      # the number of sides of a block, one letter each
    alphabet = instance["alphabet"]        # the letters used; letter l is alphabet[l]
    num_letters = instance["num_letters"]  # the number of letters on the blocks
    words_str = instance["words_str"]      # the words that must be spelled

    # Each word as the positions of its letters in the alphabet.
    words = [[alphabet.index(c) for c in word] for word in words_str]

    pool = IDPool()
    # dice[l] is the block (0 to num_blocks - 1) that carries letter l
    dice = [Integer(f"dice{l}", 0, num_blocks - 1, vpool=pool) for l in range(num_letters)]
    engine = IntegerEngine(vars=dice, vpool=pool)

    # A block shows one letter at a time, so the letters of a word sit on different blocks.
    for word in words:
        engine.add_alldifferent([dice[letter] for letter in word])
    cnf = engine.clausify()

    # Every block carries exactly num_sides letters.
    for block in range(num_blocks):
        cnf.extend(CardEnc.equals(lits=[dice[letter].equals(block) for letter in range(num_letters)],
                                  bound=num_sides, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    return cnf, {"dice": dice}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

# csplib_033_word_design: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_033_word_design.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_033_word_design.py csplib_033_word_design.json

from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

A, C, G, T = 1, 2, 3, 4  # the four letters, numbered 1 to 4 in the order A, C, G, T
CG_PER_WORD = 4          # every word has exactly this many letters that are C or G
MIN_DISTANCE = 4         # any two words differ in at least this many positions


def create_model(instance):
    """Find num_words words of length n over the letters A, C, G, T such that every word has four
    letters from {C, G}, any two different words differ in at least four positions, and the
    reverse of any word x differs from the Watson-Crick complement of any word y (x and y may be
    the same word) in at least four positions."""
    n = instance["n"]                 # the length of each word
    n_words = instance["num_words"]   # the number of words in the set

    pool = IDPool()
    # words[i][j] is the letter at position j of word i
    words = [[Integer(f"word{i}_{j}", A, T, vpool=pool) for j in range(n)]
             for i in range(n_words)]
    engine = IntegerEngine(vars=[letter for word in words for letter in word], vpool=pool)
    cnf = engine.clausify()
    # is_letter[i][j][a] is true when position j of word i holds letter a
    is_letter = [[{a: words[i][j].equals(a) for a in range(A, T + 1)} for j in range(n)]
                 for i in range(n_words)]

    def at_least_differ(first, second, key):
        """Require that the letters of first and second differ in at least MIN_DISTANCE positions."""
        # differ[j] can only be true where the two words hold different letters at position j,
        # which is all that the count needs
        differ = []
        for j in range(n):
            flag = pool.id((key, j))
            for a in range(A, T + 1):
                cnf.append([-flag, -first[j][a], -second[j][a]])
            differ.append(flag)
        cnf.extend(CardEnc.atleast(lits=differ, bound=MIN_DISTANCE, vpool=pool,
                                   encoding=EncType.seqcounter).clauses)

    # Each word has exactly CG_PER_WORD letters that are C or G. A position holds one letter,
    # so each position is counted at most once.
    for i in range(n_words):
        lits = [is_letter[i][j][a] for j in range(n) for a in (C, G)]
        cnf.extend(CardEnc.equals(lits=lits, bound=CG_PER_WORD, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    # Any two different words differ in at least MIN_DISTANCE positions.
    for x, y in combinations(range(n_words), 2):
        at_least_differ(is_letter[x], is_letter[y], ("differ", x, y))

    # For any words x and y (x = y included), the letters of x read backwards differ from the
    # Watson-Crick complement of y in at least MIN_DISTANCE positions. The complement turns each
    # letter v into 5 - v, so A and T swap and C and G swap.
    for x in range(n_words):
        reverse_x = [is_letter[x][n - 1 - j] for j in range(n)]
        for y in range(n_words):
            complement_y = [{a: is_letter[y][j][T + A - a] for a in range(A, T + 1)}
                            for j in range(n)]
            at_least_differ(reverse_x, complement_y, ("rc", x, y))

    return cnf, {"words": words}


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

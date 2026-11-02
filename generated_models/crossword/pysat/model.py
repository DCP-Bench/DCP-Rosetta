# crossword: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python crossword.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# The 15 words the slots are filled from.
WORDS = [
    "HOSES", "LASER", "SAILS", "SHEET", "STEER",
    "HEEL", "HIKE", "KEEL", "KNOT", "LINE",
    "AFT", "ALE", "EEL", "LEE", "TIE",
]
# The most letters a word has. Shorter words are padded to this length.
WORD_LEN = 5
# The eight numbered slots of the grid, each to be filled with one word.
N_SLOTS = 8
# The crossings of the grid. Where two slots cross, the word in slot a has the shared
# letter at position pos_a, and the word in slot b has it at position pos_b.
CROSSINGS = [
    [0, 2, 1, 0], [0, 4, 2, 0], [3, 1, 1, 2], [3, 2, 4, 0], [3, 3, 2, 2], [6, 0, 1, 3],
    [6, 1, 4, 1], [6, 2, 2, 3], [7, 0, 5, 1], [7, 2, 1, 4], [7, 3, 4, 2], [7, 4, 2, 4],
]


def create_model(instance):
    """Complete a crossword grid with 8 words chosen from a list of 15 words, so that
    where two words cross they share the same letter."""
    # letters[w][p]: the letter at position p of word w, numbered A=1 to Z=26, and 0
    # past the end of a shorter word.
    letters = [[ord(ch) - ord("A") + 1 for ch in word] + [0] * (WORD_LEN - len(word)) for word in WORDS]
    # The number of words in the list.
    n_words = len(WORDS)

    pool = IDPool()
    # E[s] is the word that fills slot s, as its position in WORDS.
    E = [Integer(f"E_{s}", 0, n_words - 1, vpool=pool) for s in range(N_SLOTS)]
    engine = IntegerEngine(vars=E, vpool=pool)
    # Each word is used in at most one slot, so the slots hold different words.
    engine.add_alldifferent(E)
    formula = engine.clausify()

    # Where two slots cross, their words have the same letter in the shared cell. Each
    # pair of words that disagree at a crossing is ruled out.
    for slot_a, pos_a, slot_b, pos_b in CROSSINGS:
        for word_a in range(n_words):
            for word_b in range(n_words):
                if letters[word_a][pos_a] != letters[word_b][pos_b]:
                    formula.append([-E[slot_a].equals(word_a), -E[slot_b].equals(word_b)])

    return formula, {"E": E}


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

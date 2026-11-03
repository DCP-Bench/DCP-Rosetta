"""Crossword: choose 8 of the 15 words to fill the numbered slots of the grid, crossing letters agreeing."""
import hexaly.optimizer as hx

# The words from the problem statement, longest first and then alphabetical, so that word 0 is HOSES
WORDS = sorted(["AFT", "ALE", "EEL", "HEEL", "HIKE", "HOSES", "KEEL", "KNOT", "LASER", "LEE", "LINE",
                "SAILS", "SHEET", "STEER", "TIE"], key=lambda w: (-len(w), w))
# The slots 1..8 of the grid and their lengths: 1 across, 2 down, 3 down, 4 across, 5 down, 6 down,
# 7 across and 8 across
LENGTHS = [5, 5, 5, 4, 4, 3, 3, 5]
# Crossings as (slot, letter of it, slot, letter of it), read off the grid
CROSSINGS = [(1, 2, 2, 0), (1, 4, 3, 0),
             (2, 2, 4, 1), (2, 3, 7, 0), (2, 4, 8, 2),
             (3, 2, 4, 3), (3, 3, 7, 2), (3, 4, 8, 4),
             (5, 0, 4, 2), (5, 1, 7, 1), (5, 2, 8, 3),
             (6, 1, 8, 0)]


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # E[k] is the word (numbered as above) placed in slot k + 1, and has that slot's length
    E = [model.int(min(i for i, w in enumerate(WORDS) if len(w) == n),
                   max(i for i, w in enumerate(WORDS) if len(w) == n)) for n in LENGTHS]
    # Eight different words are selected
    for a in range(8):
        for b in range(a + 1, 8):
            model.constraint(E[a] != E[b])

    def letter(slot, k):
        """The code of letter k of the word in slot (1-based), looked up from the word list."""
        codes = model.array([ord(w[k]) if k < len(w) else 0 for w in WORDS])
        return model.at(codes, E[slot - 1])

    # Where two slots cross, the letters agree
    for slot_a, k_a, slot_b, k_b in CROSSINGS:
        model.constraint(letter(slot_a, k_a) == letter(slot_b, k_b))

    return optimizer, {"E": E}

# crossword: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crossword.html
# Run it (after `pip install pulp numpy`) with:
#   python crossword.py

import pulp


def create_model(instance):
    """Fill the eight slots of a small crossword grid with eight different words chosen
    from a list of fifteen, so that where two slots cross they share the same letter."""
    # The fifteen words to fill the slots from.
    words = ["HOSES", "LASER", "SAILS", "SHEET", "STEER", "HEEL", "HIKE", "KEEL", "KNOT",
             "LINE", "AFT", "ALE", "EEL", "LEE", "TIE"]
    n_words = len(words)
    longest = max(len(word) for word in words)
    # letters[w][p]: letter p of word w, counting A as 1
    letters = [[ord(ch) - ord("A") + 1 for ch in word] + [0] * (longest - len(word))
               for word in words]
    # The eight numbered slots of the grid.
    n_slots = 8
    # Each crossing is a cell shared by two slots, as (slot a, position in a, slot b, position in b).
    crossings = [
        (0, 2, 1, 0), (0, 4, 2, 0),
        (3, 1, 1, 2), (3, 2, 4, 0), (3, 3, 2, 2),
        (6, 0, 1, 3), (6, 1, 4, 1), (6, 2, 2, 3),
        (7, 0, 5, 1), (7, 2, 1, 4), (7, 3, 4, 2), (7, 4, 2, 4),
    ]

    problem = pulp.LpProblem("crossword", pulp.LpMinimize)

    # put[s][w] is 1 when word w fills slot s, and 0 when not
    put = [[pulp.LpVariable(f"put_{s}_{w}", cat="Binary") for w in range(n_words)]
           for s in range(n_slots)]

    # The letter at position place of the word in the given slot.
    def letter(slot, place):
        return pulp.lpSum(letters[w][place] * put[slot][w] for w in range(n_words))

    # Each slot is filled with exactly one word.
    for s in range(n_slots):
        problem += pulp.lpSum(put[s]) == 1

    # No word fills two slots.
    for w in range(n_words):
        problem += pulp.lpSum(put[s][w] for s in range(n_slots)) <= 1

    # Where two slots cross, the word in each has the same letter in the shared cell.
    for s1, p1, s2, p2 in crossings:
        problem += letter(s1, p1) == letter(s2, p2)

    # E[s] is the word that fills slot s.
    E = [pulp.lpSum(w * put[s][w] for w in range(n_words)) for s in range(n_slots)]
    return problem, {"E": E}


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

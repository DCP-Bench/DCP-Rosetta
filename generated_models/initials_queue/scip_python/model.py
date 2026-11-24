# initials_queue: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python initials_queue.py

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Ten people stand in a queue, and each has initials that are an alphabetically
    ordered pair of distinct letters from the first five letters A to E (A=0 ... E=4).
    No two people have the same initials, and no two people next to each other in the
    queue share a letter. BE is at the front, CD is second, and BD is at the back.
    Find the initials of the ten people, starting from the front.

    The instance file is empty ([]), so the instance argument holds no data and is not
    read: the statement fixes everything.
    """
    letters = 5  # the first five letters of the alphabet, A to E, coded 0 to 4

    # Every alphabetical pair (a, b) with a < b, from the five letters: C(5, 2) = 10 pairs.
    pairs = [(a, b) for a in range(letters) for b in range(a + 1, letters)]
    # The statement has ten people. Their initials are all different and there are exactly
    # ten pairs, so the ten people use every pair once.
    people = len(pairs)

    # incidence[k, c] = 1 when letter c is in pairs[k], so incidence[k] lists the letters of a pair.
    incidence = np.array([[c in pair for c in range(letters)] for pair in pairs], dtype=int)

    model = Model("initials_queue")

    # at[p, k] = 1 when the person at queue position p (0 = front) has the initials pairs[k].
    at = model.addMatrixVar((people, people), vtype="B", name="at")
    model.addMatrixCons(at.sum(axis=1) == 1)  # each position holds exactly one pair
    model.addMatrixCons(at.sum(axis=0) == 1)  # each pair is held by exactly one position

    # letter_in[p, c] = 1 when the person at position p has letter c in their initials.
    # This is a linear expression, not a variable: it is the sum of at over the pairs with c.
    letter_in = at @ incidence

    # Neighbours in the queue share no letter: for each letter, the counts at positions p and p+1
    # add to at most 1, so the letter is not in both people's initials.
    model.addMatrixCons(letter_in[:-1] + letter_in[1:] <= 1)

    # The fixed front of the queue: BE at position 0, CD at position 1, and BD at the last position.
    # Letters B, C, D, E are coded 1, 2, 3, 4.
    model.addCons(at[0, pairs.index((1, 4))] == 1)  # BE at the front
    model.addCons(at[1, pairs.index((2, 3))] == 1)  # CD right behind
    model.addCons(at[people - 1, pairs.index((1, 3))] == 1)  # BD at the end of the queue

    # Output: the initials of each position, as its two letter codes. The pair at a position
    # is the sum over the pairs of at times that pair's letters.
    queue = at @ np.array(pairs)

    return model, {"queue": queue}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

# ages_of_the_sons: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install cvc5 numpy`) with:
#   python ages_of_the_sons.py

import cvc5.pythonic as c5


def create_model(instance):
    """An old man says the product of his three sons' ages is 36. Knowing the sum
    of the ages is still not enough for a mathematician to find them, but once
    told that the oldest son has blue eyes (so there is a unique oldest) he can.
    What are the ages of the three sons?"""
    # The ages of the oldest, middle and youngest son.
    A1, A2, A3 = c5.Ints("A1 A2 A3")

    # Candidate triples: ages, oldest first, whole numbers from 1 up, with product 36.
    # No age can exceed 36, since the other two are at least 1.
    cands = [
        (a, b, c)
        for a in range(1, 37)
        for b in range(1, a + 1)
        for c in range(1, b + 1)
        if a * b * c == 36
    ]

    # The oldest son is strictly older than the second son.
    def unique_oldest(t):
        return t[0] > t[1]

    # Another candidate has the same sum.
    def sum_is_shared(t):
        s = sum(t)
        return sum(1 for u in cands if sum(u) == s) >= 2

    # Candidates that fit the clues so far: a unique oldest son, and a sum that another candidate shares.
    survivors = [t for t in cands if unique_oldest(t) and sum_is_shared(t)]

    solver = c5.Solver()

    solver.add(
        # The sons' ages are whole numbers from 1 up, oldest first.
        A3 >= 1,
        A1 >= A2,
        A2 >= A3,
        # The ages are one of the candidate triples.
        c5.Or([c5.And(A1 == a, A2 == b, A3 == c) for a, b, c in cands]),
        # Another candidate has the same sum as the sons, so the sum alone does not settle the ages.
        c5.Or([
            c5.And(A1 + A2 + A3 == a + b + c, c5.Or(A1 != a, A2 != b, A3 != c))
            for a, b, c in cands
        ]),
        # The oldest son is identified by his blue eyes, so no other son has his age.
        A1 > A2,
        # Among the candidates that fit the clues so far, the sum of the true ages picks out one.
        *[
            c5.Implies(A1 + A2 + A3 == a + b + c, c5.And(A1 == a, A2 == b, A3 == c))
            for a, b, c in survivors
        ],
    )
    return solver, {"A1": A1, "A2": A2, "A3": A3}


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

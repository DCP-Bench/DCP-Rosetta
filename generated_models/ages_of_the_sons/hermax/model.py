# ages_of_the_sons: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install hermax`) with:
#   python ages_of_the_sons.py

from hermax.model import Model

# Fixed by the statement: the product of the three ages.
PRODUCT = 36


def create_model(instance):
    """Find the ages of an old man's three sons, oldest first.

    Clues, in the statement's order: (1) the product of the ages is 36; (2) the sum of
    the ages equals the number of windows, and the mathematician still needs more
    information, so another triple of ages with product 36 has the same sum; (3) the
    oldest son is unique and has blue eyes, so the mathematician can tell which triple
    it is, because the other triple has no unique oldest.
    """
    # The instance file is empty: every number comes from the statement, so the
    # instance argument is not read.
    m = Model()

    # ages[k] is the age of son k+1, oldest first, so ages[0] >= ages[1] >= ages[2] >= 1
    ages = m.int_vector("A", 3, 1, PRODUCT)

    # All triples of ages, oldest first, whose product is 36. Ages are whole numbers
    # from 1 up, and none can exceed 36.
    triples = [(a, b, c)
               for a in range(1, PRODUCT + 1)
               for b in range(1, a + 1)
               for c in range(1, b + 1)
               if a * b * c == PRODUCT]

    # Clue 1: the product of the ages is 36.
    m &= m.table(ages, allowed=triples)

    # Clue 2: the mathematician could not decide from the sum, so there is another
    # triple of ages with product 36 and the same sum. We name it, oldest first.
    others = m.int_vector("B", 3, 1, PRODUCT)  # others[k] is the age of the other triple's k+1 member
    # Clue 3: the oldest son is unique. The other triple must have its oldest
    # not unique (two sons share the top age), or the blue-eyes clue would already
    # have decided the case for the mathematician.
    m &= m.table(others, allowed=[t for t in triples if t[0] == t[1]])
    # The other triple has the same sum as the actual one.
    m &= (ages[0] + ages[1] + ages[2] == others[0] + others[1] + others[2])

    # Clue 3 for the actual sons: the oldest son is unique, so ages[0] > ages[1].
    m &= (ages[1] + 1 <= ages[0])

    return m, {"A1": ages[0], "A2": ages[1], "A3": ages[2]}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

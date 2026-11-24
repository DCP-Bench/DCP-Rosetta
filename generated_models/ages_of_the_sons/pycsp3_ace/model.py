# ages_of_the_sons: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python ages_of_the_sons.py

from pycsp3 import *


def create_model(instance):
    """An old man asks a mathematician to guess the ages of his three sons. The product
    of their ages is 36; the sum of their ages is the number of windows in a building he
    points to. The mathematician needs more information after each of the first two
    statements. The oldest son has blue eyes, and then the mathematician knows the ages.
    Find the ages of the three sons, oldest first."""
    # the number of sons (the statement)
    n_sons = 3
    # the product of the three ages (the statement)
    product = 36

    # Every way to write the product as three positive ages, oldest first. The oldest age
    # is at most the product, since the other two ages are at least 1.
    candidates = [
        (oldest, middle, youngest)
        for oldest in range(1, product + 1)
        for middle in range(1, oldest + 1)
        for youngest in range(1, middle + 1)
        if oldest * middle * youngest == product
    ]

    # The candidates whose oldest son is unique: only for these can the blue-eyed son be identified.
    unique_oldest = [candidate for candidate in candidates if candidate[0] > candidate[1]]

    # The ages of the sons, oldest first: one of the candidate triples.
    ages = VarArray(size=n_sons, dom=range(1, product + 1))
    # The number of windows: the sum of the sons' ages. The smallest sum is n_sons, since every
    # age is at least 1; the largest is product + n_sons - 1, from ages product, 1, 1 (any other
    # split of the product into three ages has a smaller sum).
    min_sum = n_sons
    max_sum = product + n_sons - 1
    windows = Var(dom=range(min_sum, max_sum + 1))
    # rival: another candidate triple with the same sum as ages; the mathematician cannot rule it out once he hears the sum.
    rival = VarArray(size=n_sons, dom=range(1, product + 1))
    # matches[k] is 1 when the k-th candidate with a unique oldest son has a sum equal to the number of windows.
    matches = VarArray(size=len(unique_oldest), dom={0, 1})

    # The mathematician's first "I need more information" gives no constraint: every candidate
    # triple has the same product, and there is more than one such triple.
    satisfy(
        # The product of the ages is 36, so the ages are one of the candidate triples.
        Table(scope=ages, supports=candidates),
        # The sum of the ages is the number of windows.
        Sum(ages) == windows,
        # The oldest son is unique: the blue-eyed son can be singled out only when no other son
        # is as old as he is.
        ages[0] > ages[1],
        # After the sum, the mathematician still cannot tell the ages: another candidate triple
        # has the same sum, and it is a different triple.
        Table(scope=rival, supports=candidates),
        Sum(rival) == windows,
        Hamming(ages, rival) >= 1,
        # The oldest son has blue eyes, so the mathematician knows the ages: exactly one
        # candidate with a unique oldest son has this sum.
        [matches[k] == (windows == sum(candidate)) for k, candidate in enumerate(unique_oldest)],
        Count(matches, value=1) == 1,
    )

    return {"A1": ages[0], "A2": ages[1], "A3": ages[2]}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())

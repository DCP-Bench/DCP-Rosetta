# ages_of_the_sons: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python ages_of_the_sons.py

from pyscipopt import Model


def create_model(instance):
    """An old man has three sons, each of a whole-number age, and a mathematician has
    to work out their ages from three clues, which the old man gives in this order:
      1. the product of their ages is 36;
      2. the sum of their ages equals the number of windows in the building. The
         mathematician says that is not enough: he still needs more information,
         because another set of three ages has the same sum and the same product;
      3. the oldest son has blue eyes, so there is a single oldest son.
    The answer is the ages of the three sons, oldest first. The instance holds no data
    (the statement fixes everything), so the model reads nothing from it."""

    model = Model("ages_of_the_sons")

    # The product of the ages is fixed by the statement: "the product of their ages is 36".
    PRODUCT = 36

    # A1, A2, A3 are the ages of the oldest, middle and youngest son.
    # Each age is a whole number from 1 up to PRODUCT: every age is at least 1, so
    # the product of the three ages bounds each one by PRODUCT.
    A1 = model.addVar(name="A1", vtype="I", lb=1, ub=PRODUCT)  # age of the oldest son
    A2 = model.addVar(name="A2", vtype="I", lb=1, ub=PRODUCT)  # age of the middle son
    A3 = model.addVar(name="A3", vtype="I", lb=1, ub=PRODUCT)  # age of the youngest son

    # Clue 1: the product of their ages is 36.
    model.addCons(A1 * A2 * A3 == PRODUCT, name="product_is_36")

    # The ages are listed oldest first, so the youngest is listed last: A2 >= A3 (output order, not a clue).
    model.addCons(A2 >= A3, name="output_order")

    # Clue 2: the sum of their ages equals the number of windows in the building. The
    # number of windows is not given, so the sum is free; the clue only says that more
    # than one set of ages has that same sum. B1, B2, B3 are that other set of ages,
    # with the same product and the same sum.
    B1 = model.addVar(name="B1", vtype="I", lb=1, ub=PRODUCT)  # oldest age in the other set
    B2 = model.addVar(name="B2", vtype="I", lb=1, ub=PRODUCT)  # middle age in the other set
    B3 = model.addVar(name="B3", vtype="I", lb=1, ub=PRODUCT)  # youngest age in the other set
    model.addCons(B1 * B2 * B3 == PRODUCT, name="other_product_is_36")  # the other set also multiplies to 36
    model.addCons(B1 + B2 + B3 == A1 + A2 + A3, name="same_sum_as_windows")  # and the same sum

    # Clue 2 (cont.): the other set is a different set of ages, so its oldest age differs from A1.
    # Sort the other set oldest first, so that it is counted once and B1 is its oldest age;
    # the B1 != A1 test below depends on this.
    model.addCons(B1 >= B2, name="other_sorted_1")
    model.addCons(B2 >= B3, name="other_sorted_2")
    # d = 1: B1 > A1, d = 0: B1 < A1 (SCIP has no != constraint, so the disequality is
    # two indicators on one binary). With the same sum and product, an equal oldest age
    # would force the same other two ages, so B1 != A1 is exactly "a different set of ages".
    d = model.addVar(name="other_oldest_is_higher", vtype="B")  # auxiliary selector
    model.addConsIndicator(B1 <= A1 - 1, binvar=d, activeone=False, name="other_oldest_lower")
    model.addConsIndicator(B1 >= A1 + 1, binvar=d, name="other_oldest_higher")

    # Clue 3: the oldest son has blue eyes, so he is the only one of his age:
    # A1 is strictly older than A2.
    model.addCons(A1 >= A2 + 1, name="single_oldest_son")

    return model, {"A1": A1, "A2": A2, "A3": A3}


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

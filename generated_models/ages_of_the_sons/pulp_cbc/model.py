# ages_of_the_sons: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install pulp numpy`) with:
#   python ages_of_the_sons.py

import pulp


def create_model(instance):
    """An old man says the product of his three sons' ages is 36. Knowing the sum
    of the ages is still not enough for a mathematician to find them, but once
    told that the oldest son has blue eyes (so there is a unique oldest) he can.
    What are the ages of the three sons?"""
    # The product of the three ages, from the statement.
    product = 36
    # No son is older than 36: every age is at least 1, and the product is 36.
    max_age = 36
    # Larger than any difference between two ages, so it switches off a comparison.
    big_m = max_age + 1

    problem = pulp.LpProblem("ages_of_the_sons", pulp.LpMinimize)

    # Every set of three ages, oldest first, whose product is 36.
    triples = [(a, b, c) for a in range(max_age + 1) for b in range(a + 1) for c in range(b + 1)
               if a * b * c == product]

    def choose_triple(name):
        # pick[t] is 1 when the triple t is the chosen set of ages.
        pick = {t: pulp.LpVariable(f"{name}_{t[0]}_{t[1]}_{t[2]}", cat="Binary")
                for t in triples}
        # The ages of the chosen triple, oldest first.
        ages = [pulp.lpSum(t[k] * var for t, var in pick.items()) for k in range(3)]
        return pick, ages

    # The sons' ages are one of the triples.
    pick_a, (a1, a2, a3) = choose_triple("A")
    problem += pulp.lpSum(pick_a.values()) == 1
    # The other triple of ages, which also has product 36, is one of the triples too.
    pick_b, (b1, b2, b3) = choose_triple("B")
    problem += pulp.lpSum(pick_b.values()) == 1

    # The age of the oldest, middle and youngest son.
    A1 = pulp.LpVariable("A1", 0, max_age, cat="Integer")
    A2 = pulp.LpVariable("A2", 0, max_age, cat="Integer")
    A3 = pulp.LpVariable("A3", 0, max_age, cat="Integer")
    # The sons' ages are the chosen triple.
    problem += A1 == a1
    problem += A2 == a2
    problem += A3 == a3

    # The oldest son is unique: A1 is strictly older than A2.
    problem += A1 >= A2 + 1

    # b_older is 1 when the oldest of the other triple is older than the sons' oldest, and 0 when not.
    b_older = pulp.LpVariable("b_older", cat="Binary")
    # The oldest ages of the two triples differ, and b_older says which one is older.
    problem += A1 <= b1 - 1 + big_m * (1 - b_older)
    problem += A1 >= b1 + 1 - big_m * b_older

    # The other triple has the same sum of ages, so the sum alone does not decide the ages.
    problem += A1 + A2 + A3 == b1 + b2 + b3

    return problem, {"A1": A1, "A2": A2, "A3": A3}


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

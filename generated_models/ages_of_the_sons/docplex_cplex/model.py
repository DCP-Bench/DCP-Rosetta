# ages_of_the_sons: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python ages_of_the_sons.py

from docplex.mp.model import Model


def create_model(instance):
    """Ages of the sons: the ages of an old man's three sons multiply to 36. Their sum, the number of
    windows of a building, is still not enough to tell the ages, so another triple of ages with
    product 36 has the same sum. Then the oldest son is told apart: he is older than his brothers.
    What are the three ages?"""
    product = 36  # product of the ages (puzzle constant)
    top = product  # an age is at most the product, since the other two ages are at least 1

    model = Model("ages_of_the_sons")

    # A product of three variables is not linear. It is stated as a table: the triples
    # x1 >= x2 >= x3 in 0..36 whose product is 36, of which exactly one is chosen.
    triples = [(x1, x2, x3) for x1 in range(top + 1) for x2 in range(x1 + 1) for x3 in range(x2 + 1)
               if x1 * x2 * x3 == product]

    # pick_a[t] is 1 when t = (A1, A2, A3) are the sons' ages, from the oldest: the oldest is strictly
    # older than the second, who is at least as old as the third, and the ages multiply to 36.
    pick_a = {t: model.binary_var(name=f"a_{t[0]}_{t[1]}_{t[2]}") for t in triples if t[0] > t[1]}
    model.add_constraint(model.sum(pick_a.values()) == 1)

    # pick_b[t] is 1 when t is the other triple of ages (oldest first) with product 36.
    pick_b = {t: model.binary_var(name=f"b_{t[0]}_{t[1]}_{t[2]}") for t in triples}
    model.add_constraint(model.sum(pick_b.values()) == 1)

    def age(pick, k):  # the k-th age (0 is the oldest) of the triple chosen in pick
        return model.sum(t[k] * v for t, v in pick.items())

    # The other triple has a different oldest age ...
    model.add_constraint(age(pick_a, 0) != age(pick_b, 0))

    # ... and the same sum, so the number of windows does not settle the question.
    model.add_constraint(age(pick_a, 0) + age(pick_a, 1) + age(pick_a, 2)
                         == age(pick_b, 0) + age(pick_b, 1) + age(pick_b, 2))

    return model, {"A1": age(pick_a, 0), "A2": age(pick_a, 1), "A3": age(pick_a, 2)}


if __name__ == "__main__":
    model, outputs = create_model({})
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)

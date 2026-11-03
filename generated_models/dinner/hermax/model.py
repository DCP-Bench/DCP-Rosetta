# dinner: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install hermax`) with:
#   python dinner.py

from hermax.model import Model


def create_model(instance):
    """Choose how many grandparents, parents and children go out to dinner: 1-6 grandparents,
    1-10 parents and 1-40 children, 20 people in all, costing exactly $20 in total, with
    grandparents at $3, parents at $2 and children at $0.50 each."""
    # The instance carries no data: every number here is fixed by the problem statement.
    m = Model()

    # How many of each kind go to dinner; the ranges are the ones in the statement.
    grandparents = m.int("grandparents", 1, 6)  # grandparents going to dinner
    parents = m.int("parents", 1, 10)           # parents going to dinner
    children = m.int("children", 1, 40)         # children going to dinner

    # There must be 20 people at dinner in all.
    m &= (grandparents + parents + children == 20)
    # The dinner must cost exactly $20. Prices are in cents to stay integral:
    # $3 = 300 cents, $2 = 200 cents, $0.50 = 50 cents.
    m &= (300 * grandparents + 200 * parents + 50 * children == 2000)

    return m, {"grandparents": grandparents, "parents": parents, "children": children}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

# bananas: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install exact numpy`) with:
#   python bananas.py

from exact import Exact


def create_model(instance):
    """Buy 100 fruits for 100 dollars, at least one of each kind: five bananas cost
    3 dollars, seven oranges 5 dollars, nine mangoes 7 dollars and three apples 9
    dollars. Bananas and apples are disliked, so buy as few of them as possible."""
    # Price of one fruit in 1/945 dollar, so that the prices are whole numbers:
    # banana 3/5 dollar = 567, orange 5/7 = 675, mango 7/9 = 735, apple 9/3 = 2835.
    prices = [567, 675, 735, 2835]

    solver = Exact()

    # Exact identifies its variables by name.
    # The four kinds of fruit, in the order of prices.
    fruits = ["bananas", "oranges", "mangoes", "apples"]
    # The number of each kind bought, from 1 to 100.
    for name in fruits:
        solver.addVariable(name, 1, 100)

    # the_sum is the number of bananas and apples bought, from 2 to 200.
    solver.addVariable("the_sum", 2, 200)
    solver.addConstraint([(1, "bananas"), (1, "apples"), (-1, "the_sum")], True, 0, True, 0)

    # Buy 100 fruits in total.
    solver.addConstraint([(1, name) for name in fruits], True, 100, True, 100)

    # They cost exactly 100 dollars, which is 94500 in units of 1/945 dollar.
    solver.addConstraint([(price, name) for price, name in zip(prices, fruits)], True, 94500, True, 94500)

    # Buy as few bananas and apples as possible.
    solver.setObjective([(1, "the_sum")], minimize=True)

    return solver, {name: name for name in fruits}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

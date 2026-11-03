# bananas: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bananas.html
# Run it (after `pip install pychoco numpy`) with:
#   python bananas.py

from pychoco.model import Model


def create_model(instance):
    """Buy 100 fruits for exactly 100 dollars, at least one of each kind. Bananas cost
    3 dollars for 5, oranges 5 dollars for 7, mangoes 7 dollars for 9 and apples 9 dollars
    for 3. Buy as few bananas and apples as possible."""
    n_fruits = 100  # the number of fruits to buy
    # Price of one fruit in units of 1/945 dollar, so that every price is a whole number:
    # banana 3/5 dollar = 567, orange 5/7 = 675, mango 7/9 = 735, apple 9/3 = 2835.
    prices = [567, 675, 735, 2835]
    budget = 100 * 945  # 100 dollars in the same units

    model = Model()

    # the number of bananas, oranges, mangoes and apples bought, at least one of each kind
    x = [model.intvar(1, n_fruits, name=name) for name in ("bananas", "oranges", "mangoes", "apples")]
    bananas, oranges, mangoes, apples = x

    # The fruits cost exactly 100 dollars.
    model.scalar(x, prices, "=", budget).post()

    # Exactly 100 fruits are bought.
    model.sum(x, "=", n_fruits).post()

    # The bananas and apples bought, which is the number to minimise.
    disliked = model.intvar(2, 2 * n_fruits, name="disliked")
    model.sum([bananas, apples], "=", disliked).post()

    return (model,
            {"bananas": bananas, "oranges": oranges, "mangoes": mangoes, "apples": apples},
            {"objective": disliked, "maximize": False})


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")

# contracting_costs: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/contracting_costs.html
# Run it (after `pip install pychoco numpy`) with:
#   python contracting_costs.py

from pychoco.model import Model


def create_model(instance):
    """A contractor planning the construction of a house has to pay six pairs of tradesmen a known sum for each pair. What does each man charge for his services?"""
    # The sum paid for each pair of tradesmen, in dollars.
    bills = [
        ("paper_hanger", "painter", 1100),
        ("painter", "plumber", 1700),
        ("plumber", "electrician", 1100),
        ("electrician", "carpenter", 3300),
        ("carpenter", "mason", 5300),
        ("mason", "painter", 3200),
    ]
    # The largest bill; no man charges more than this.
    largest = max(amount for _, _, amount in bills)

    model = Model()

    # The six tradesmen, with what each charges in dollars; each charges at least $1.
    men = ["paper_hanger", "painter", "plumber", "electrician", "carpenter", "mason"]
    charge = {man: model.intvar(1, largest, name=man) for man in men}

    # Each pair's two charges add up to the sum paid for that pair.
    for first, second, amount in bills:
        model.arithm(charge[first], "+", charge[second], "=", amount).post()

    return model, charge, None


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

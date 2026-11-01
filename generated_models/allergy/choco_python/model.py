# allergy: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install pychoco numpy`) with:
#   python allergy.py

from pychoco.model import Model


def create_model(instance):
    """Four friends are each allergic to something different (eggs, mold, nuts,
    ragweed) and each has a different surname (Baxter, Lemon, Malone, Fleet).
    Match each allergy and each surname to a friend, given the clues."""
    n_friends = 4  # Debra, Janet, Hugh and Rick
    # The friends are numbered Debra = 0, Janet = 1, Hugh = 2, Rick = 3.
    debra, janet, hugh, rick = range(n_friends)

    model = Model()

    # foods[k] is the friend allergic to food k (eggs, mold, nuts, ragweed).
    foods = [model.intvar(0, n_friends - 1, name=f"food_{k}") for k in range(n_friends)]
    eggs, mold, nuts, ragweed = foods
    # surnames[k] is the friend with surname k (Baxter, Lemon, Malone, Fleet).
    surnames = [model.intvar(0, n_friends - 1, name=f"surname_{k}") for k in range(n_friends)]
    baxter, lemon, malone, fleet = surnames

    # Each friend has a different allergy and a different surname.
    model.all_different(foods).post()
    model.all_different(surnames).post()

    # Rick is not allergic to mold.
    model.arithm(mold, "!=", rick).post()
    # Baxter is allergic to eggs.
    model.arithm(eggs, "=", baxter).post()
    # Hugh is neither surnamed Lemon nor Fleet.
    model.arithm(lemon, "!=", hugh).post()
    model.arithm(fleet, "!=", hugh).post()
    # Debra is allergic to ragweed.
    model.arithm(ragweed, "=", debra).post()
    # Janet is not surnamed Lemon, and is allergic to neither eggs nor mold.
    model.arithm(lemon, "!=", janet).post()
    model.arithm(eggs, "!=", janet).post()
    model.arithm(mold, "!=", janet).post()

    return model, {
        "eggs": eggs,
        "mold": mold,
        "nuts": nuts,
        "ragweed": ragweed,
        "baxter": baxter,
        "lemon": lemon,
        "malone": malone,
        "fleet": fleet,
    }, None


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

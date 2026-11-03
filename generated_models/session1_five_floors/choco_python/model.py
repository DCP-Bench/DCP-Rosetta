# session1_five_floors: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install pychoco numpy`) with:
#   python session1_five_floors.py

from pychoco.model import Model


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith live on different floors of a
    five-floor apartment house; find their floors from the stated clues."""
    model = Model()

    # The floor, 1 to 5, of each person. Baker does not live on the fifth floor,
    # Cooper not on the first, and Fletcher on neither the first nor the fifth.
    baker = model.intvar([1, 2, 3, 4], name="B")
    cooper = model.intvar([2, 3, 4, 5], name="C")
    fletcher = model.intvar([2, 3, 4], name="F")
    miller = model.intvar(1, 5, name="M")
    smith = model.intvar(1, 5, name="S")

    # They all live on different floors.
    model.all_different([baker, cooper, fletcher, miller, smith]).post()

    # Miller lives on a higher floor than Cooper.
    model.arithm(miller, ">", cooper).post()

    # Smith does not live on a floor next to Fletcher's.
    model.distance(smith, fletcher, "!=", 1).post()

    # Fletcher does not live on a floor next to Cooper's.
    model.distance(fletcher, cooper, "!=", 1).post()

    return model, {"B": baker, "C": cooper, "F": fletcher, "M": miller, "S": smith}, None


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

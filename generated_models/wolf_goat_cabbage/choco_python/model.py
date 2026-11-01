# wolf_goat_cabbage: a Choco-solver (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

from pychoco.model import Model


def create_model(instance):
    """A farmer must ferry a wolf, a goat and a cabbage across a river in a boat
    that carries only the farmer and one item. The wolf eats the goat and the goat
    eats the cabbage when left alone together, so find a crossing in which nothing
    is eaten."""
    n_stages = instance["stage"]  # the number of stages, including the first and the last

    model = Model()

    # wolf_pos[i] is true when the wolf is on the destination shore at stage i
    wolf_pos = [model.boolvar(name=f"wolf_{i}") for i in range(n_stages)]
    # goat_pos[i] is true when the goat is on the destination shore at stage i
    goat_pos = [model.boolvar(name=f"goat_{i}") for i in range(n_stages)]
    # cabbage_pos[i] is true when the cabbage is on the destination shore at stage i
    cabbage_pos = [model.boolvar(name=f"cabbage_{i}") for i in range(n_stages)]
    # boat_pos[i] is true when the boat, and so the farmer, is on the destination shore at stage i
    boat_pos = [model.boolvar(name=f"boat_{i}") for i in range(n_stages)]

    # Everything starts on the starting shore.
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        model.arithm(pos[0], "=", 0).post()

    # Everything ends on the destination shore.
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        model.arithm(pos[-1], "=", 1).post()

    # The boat crosses the river at every stage.
    for i in range(1, n_stages):
        model.arithm(boat_pos[i], "!=", boat_pos[i - 1]).post()

    # The wolf and the goat are never left alone together: if they share a shore,
    # the boat (with the farmer) is on it too.
    for i in range(n_stages):
        model.or_([model.arithm(goat_pos[i], "!=", wolf_pos[i]),
                   model.arithm(boat_pos[i], "=", wolf_pos[i])]).post()

    # Likewise the goat and the cabbage.
    for i in range(n_stages):
        model.or_([model.arithm(goat_pos[i], "!=", cabbage_pos[i]),
                   model.arithm(boat_pos[i], "=", goat_pos[i])]).post()

    # The boat carries at most one item per crossing: between two stages, at most
    # one of the wolf, the goat and the cabbage changes shore.
    for i in range(n_stages - 1):
        # The items that change shore at this crossing.
        moved = [model.arithm(pos[i], "!=", pos[i + 1]).reify()
                 for pos in (wolf_pos, goat_pos, cabbage_pos)]
        model.sum(moved, "<=", 1).post()

    return model, {"wolf_pos": wolf_pos, "goat_pos": goat_pos,
                   "cabbage_pos": cabbage_pos, "boat_pos": boat_pos}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
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

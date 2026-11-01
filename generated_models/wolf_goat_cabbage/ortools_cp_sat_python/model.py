# wolf_goat_cabbage: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install ortools`):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A farmer must ferry a wolf, a goat and a cabbage across a river in a boat
    that carries only the farmer and one item. The wolf eats the goat and the goat
    eats the cabbage when left alone together, so find a crossing in which nothing
    is eaten."""
    n_stages = instance["stage"]  # the number of stages, including the first and the last

    model = cp_model.CpModel()

    # The shore of the wolf, the goat and the cabbage at each stage.
    wolf_pos = [model.new_bool_var(f"wolf_{i}") for i in range(n_stages)]
    goat_pos = [model.new_bool_var(f"goat_{i}") for i in range(n_stages)]
    cabbage_pos = [model.new_bool_var(f"cabbage_{i}") for i in range(n_stages)]
    # The shore of the boat, which is also the farmer's shore, at each stage.
    boat_pos = [model.new_bool_var(f"boat_{i}") for i in range(n_stages)]

    # Everything starts on the starting shore.
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        model.add(pos[0] == 0)
    # Everything ends on the destination shore.
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        model.add(pos[-1] == 1)

    # The boat crosses the river at every stage.
    for i in range(1, n_stages):
        model.add(boat_pos[i] != boat_pos[i - 1])

    for i in range(n_stages):
        # The wolf and the goat are never left alone together: if they share a shore,
        # the boat (with the farmer) is on it too.
        wolf_with_goat = model.new_bool_var(f"wolf_with_goat_{i}")
        model.add(goat_pos[i] == wolf_pos[i]).only_enforce_if(wolf_with_goat)
        model.add(goat_pos[i] != wolf_pos[i]).only_enforce_if(~wolf_with_goat)
        model.add(boat_pos[i] == wolf_pos[i]).only_enforce_if(wolf_with_goat)

        # Likewise the goat and the cabbage.
        goat_with_cabbage = model.new_bool_var(f"goat_with_cabbage_{i}")
        model.add(goat_pos[i] == cabbage_pos[i]).only_enforce_if(goat_with_cabbage)
        model.add(goat_pos[i] != cabbage_pos[i]).only_enforce_if(~goat_with_cabbage)
        model.add(boat_pos[i] == goat_pos[i]).only_enforce_if(goat_with_cabbage)

    # The boat carries at most one item per crossing: between two consecutive stages,
    # at most one of the wolf, the goat and the cabbage changes shore.
    for i in range(n_stages - 1):
        # The items that change shore at this crossing.
        moved = []
        for name, pos in (("wolf", wolf_pos), ("goat", goat_pos), ("cabbage", cabbage_pos)):
            changes = model.new_bool_var(f"{name}_changes_{i}")
            model.add(pos[i] != pos[i + 1]).only_enforce_if(changes)
            model.add(pos[i] == pos[i + 1]).only_enforce_if(~changes)
            moved.append(changes)
        model.add(sum(moved) <= 1)

    return model, {
        "wolf_pos": wolf_pos,
        "goat_pos": goat_pos,
        "cabbage_pos": cabbage_pos,
        "boat_pos": boat_pos,
    }


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

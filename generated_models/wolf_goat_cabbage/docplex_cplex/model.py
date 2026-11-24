# wolf_goat_cabbage: a CPLEX (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

from docplex.mp.model import Model


def create_model(instance):
    """Wolf, goat and cabbage: a farmer must ferry a wolf, a goat and a cabbage across a river in a boat
    that carries at most one of them besides himself, never leaving the wolf alone with the goat or
    the goat alone with the cabbage. The crossing takes a given number of stages: everything
    starts on the starting shore, ends on the destination shore, and the boat changes shore
    from each stage to the next."""
    stage = instance["stage"]  # the number of stages of the crossing
    stages = range(stage)

    model = Model("wolf_goat_cabbage")

    # wolf[i], goat[i], cabbage[i] and boat[i] are 1 when that one is on the destination shore at
    # stage i, and 0 when it is on the starting shore.
    wolf = [model.binary_var(name=f"wolf_{i}") for i in stages]
    goat = [model.binary_var(name=f"goat_{i}") for i in stages]
    cabbage = [model.binary_var(name=f"cabbage_{i}") for i in stages]
    boat = [model.binary_var(name=f"boat_{i}") for i in stages]

    # Initially everything is on the starting shore.
    for x in (boat, wolf, goat, cabbage):
        model.add_constraint(x[0] == 0)

    # The boat crosses the river at every stage.
    model.add_constraints(boat[i] + boat[i - 1] == 1 for i in range(1, stage))

    # Finally everything is on the destination shore.
    for x in (boat, wolf, goat, cabbage):
        model.add_constraint(x[-1] == 1)

    # The wolf and the goat cannot be left alone: they are never together on the shore the
    # boat is not on. On the starting shore (both 0, boat 1) and on the destination shore
    # (both 1, boat 0) this is one linear inequality each.
    model.add_constraints(boat[i] <= wolf[i] + goat[i] for i in stages)
    model.add_constraints(wolf[i] + goat[i] - boat[i] <= 1 for i in stages)

    # The goat and the cabbage cannot be left alone, in the same way.
    model.add_constraints(boat[i] <= goat[i] + cabbage[i] for i in stages)
    model.add_constraints(goat[i] + cabbage[i] - boat[i] <= 1 for i in stages)

    # Only one of the wolf, goat and cabbage can change shore per turn: the number of them
    # whose position changes is at most one. m is at least |x[i + 1] - x[i]|, the change of one
    # item: a helper variable, because the absolute value of a difference is not linear.
    for i in range(stage - 1):
        moved = []
        for name, x in (("wolf", wolf), ("goat", goat), ("cabbage", cabbage)):
            m = model.binary_var(name=f"moved_{name}_{i}")
            model.add_constraint(m >= x[i + 1] - x[i])
            model.add_constraint(m >= x[i] - x[i + 1])
            moved.append(m)
        model.add_constraint(model.sum(moved) <= 1)

    return model, {"wolf_pos": wolf, "goat_pos": goat, "cabbage_pos": cabbage, "boat_pos": boat}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
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

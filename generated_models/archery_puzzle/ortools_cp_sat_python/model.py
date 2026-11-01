# archery_puzzle: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install ortools`):
#   python archery_puzzle.py archery_puzzle.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A young archer fires as many arrows as she pleases at targets of different
    values: she wants a total score as close as possible to a target score."""
    targets = instance["targets"]            # targets[i]: the score for one hit on target i
    target_score = instance["target_score"]  # the total score she aims for
    n_targets = len(targets)                 # the number of targets

    model = cp_model.CpModel()

    # hits[i] is the number of arrows that hit target i. Every target is worth at
    # least 1 point, so more than target_score hits on one target overshoots anyway.
    hits = [model.new_int_var(0, target_score, f"hits_{i}") for i in range(n_targets)]
    score = model.new_int_var(0, target_score * 2, "score")
    deviation = model.new_int_var(0, target_score * 2, "deviation")

    # The total score is the sum of the scores of all hits.
    model.add(score == sum(t * h for t, h in zip(targets, hits)))
    # deviation is the gap between the total score and the target score.
    model.add_abs_equality(deviation, target_score - score)

    # Minimise the deviation.
    model.minimize(deviation)

    return model, {"hits": hits}


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

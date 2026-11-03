# archery_puzzle: a Choco-solver (Python) model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python archery_puzzle.py archery_puzzle.json

from pychoco.model import Model


def create_model(instance):
    """A young archer fires as many arrows as she pleases at targets of different
    values: she wants a total score as close as possible to a target score."""
    targets = instance["targets"]            # targets[i]: the points for one arrow on target i
    target_score = instance["target_score"]  # the total score she aims for
    n_targets = len(targets)                 # the number of targets

    model = Model()

    # hits[i] is the number of arrows on target i. Every target is worth at least 1
    # point, so more than target_score arrows on one target overshoots anyway.
    hits = [model.intvar(0, target_score, name=f"hits_{i}") for i in range(n_targets)]
    # score: the total score of all arrows
    score = model.intvar(0, 2 * target_score, name="score")
    # deviation: how far the total score is from the target score
    deviation = model.intvar(0, 2 * target_score, name="deviation")

    # Each arrow adds the points of its target to the total.
    model.scalar(hits, targets, "=", score).post()
    # The deviation is the distance between the total and the target score.
    model.distance(score, model.intvar(target_score, target_score), "=", deviation).post()

    # Come as close to the target score as possible.
    return model, {"hits": hits}, {"objective": deviation, "maximize": False}


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

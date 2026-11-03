# fifty_puzzle: a Choco-solver (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python fifty_puzzle.py fifty_puzzle.json

from pychoco.model import Model


def create_model(instance):
    """Dummies numbered with integers are to be knocked over with baseballs:
    choose the dummies to knock down so that their numbers add up to exactly
    the target sum, neither more nor less."""
    values = instance["values"]          # values[i]: the number on dummy i
    target_sum = instance["target_sum"]  # the sum the knocked-over numbers must reach

    model = Model()

    # dummies[i] is true when dummy i is knocked over
    dummies = [model.boolvar(name=f"dummies_{i}") for i in range(len(values))]

    # The numbers on the knocked-over dummies add up to exactly the target sum.
    model.scalar(dummies, values, "=", target_sum).post()

    return model, {"dummies": dummies}, None


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

# csplib_028_bibd: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_028_bibd.py csplib_028_bibd.json

from pychoco.model import Model


def create_model(instance):
    """Arrange n_objects objects into n_blocks blocks so that each block holds exactly
    n_objects_per_block objects, each object occurs in exactly n_blocks_per_object blocks, and
    every two distinct objects occur together in exactly n_blocks_per_pair blocks. The answer is
    the matrix of objects against blocks."""
    n_objects = instance["v"]            # the number of objects
    n_blocks = instance["b"]             # the number of blocks
    n_blocks_per_object = instance["r"]  # the number of blocks each object occurs in
    n_objects_per_block = instance["k"]  # the number of objects in each block
    n_blocks_per_pair = instance["l"]    # the number of blocks shared by any two distinct objects

    model = Model()

    # matrix[i][j] is true when object i belongs to block j
    matrix = [[model.boolvar(name=f"matrix_{i}_{j}") for j in range(n_blocks)]
              for i in range(n_objects)]

    # Every object occurs in exactly n_blocks_per_object blocks.
    for i in range(n_objects):
        model.sum(matrix[i], "=", n_blocks_per_object).post()

    # Every block holds exactly n_objects_per_block objects.
    for j in range(n_blocks):
        model.sum([matrix[i][j] for i in range(n_objects)], "=", n_objects_per_block).post()

    # Any two distinct objects occur together in exactly n_blocks_per_pair blocks.
    for i1 in range(n_objects):
        for i2 in range(i1 + 1, n_objects):
            # together[j] is true when objects i1 and i2 both belong to block j
            together = []
            for j in range(n_blocks):
                both = model.boolvar(name=f"both_{i1}_{i2}_{j}")
                model.times(matrix[i1][j], matrix[i2][j], both).post()
                together.append(both)
            model.sum(together, "=", n_blocks_per_pair).post()

    return model, {"matrix": matrix}, None


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

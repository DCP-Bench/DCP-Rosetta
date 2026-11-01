# csplib_028_bibd: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_028_bibd.py csplib_028_bibd.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Arrange v distinct objects into b blocks so that each block contains exactly k objects,
    each object occurs in exactly r blocks, and every two distinct objects occur together in
    exactly l blocks."""
    n_objects = instance["v"]            # the number of objects
    n_blocks = instance["b"]             # the number of blocks
    n_blocks_per_object = instance["r"]  # the number of blocks each object occurs in
    n_objects_per_block = instance["k"]  # the number of objects in each block
    n_blocks_per_pair = instance["l"]    # the number of blocks shared by any two distinct objects

    model = cp_model.CpModel()

    # matrix[i][j] is true when object i belongs to block j
    matrix = [[model.new_bool_var(f"matrix_{i}_{j}") for j in range(n_blocks)]
              for i in range(n_objects)]

    # Every object occurs in exactly r blocks.
    for i in range(n_objects):
        model.add(sum(matrix[i]) == n_blocks_per_object)

    # Every block contains exactly k objects.
    for j in range(n_blocks):
        model.add(sum(matrix[i][j] for i in range(n_objects)) == n_objects_per_block)

    # Any two distinct objects occur together in exactly l blocks.
    for i1 in range(n_objects):
        for i2 in range(i1 + 1, n_objects):
            # the blocks in which objects i1 and i2 occur together
            together = []
            for j in range(n_blocks):
                # true when objects i1 and i2 both belong to block j
                both = model.new_bool_var(f"both_{i1}_{i2}_{j}")
                model.add_multiplication_equality(both, [matrix[i1][j], matrix[i2][j]])
                together.append(both)
            model.add(sum(together) == n_blocks_per_pair)

    return model, {"matrix": matrix}


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

# csplib_028_bibd: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_028_bibd.py csplib_028_bibd.json

import mip


def create_model(instance):
    """Arrange v distinct objects into b blocks so that each block contains exactly k objects,
    each object occurs in exactly r blocks, and every two distinct objects occur together in
    exactly l blocks. The answer is the v-by-b incidence matrix."""
    n_objects = instance["v"]            # the number of objects
    n_blocks = instance["b"]             # the number of blocks
    n_blocks_per_object = instance["r"]  # the number of blocks each object occurs in
    n_objects_per_block = instance["k"]  # the number of objects in each block
    n_blocks_per_pair = instance["l"]    # the number of blocks in which any two objects occur together

    model = mip.Model(solver_name="CBC")

    # matrix[i][j] is 1 when object i is in block j, and 0 when not
    matrix = [[model.add_var(f"matrix_{i}_{j}", var_type=mip.BINARY) for j in range(n_blocks)]
              for i in range(n_objects)]

    # Every object occurs in exactly r blocks.
    for i in range(n_objects):
        model += mip.xsum(matrix[i][j] for j in range(n_blocks)) == n_blocks_per_object

    # Every block contains exactly k objects.
    for j in range(n_blocks):
        model += mip.xsum(matrix[i][j] for i in range(n_objects)) == n_objects_per_block

    # Every two distinct objects occur together in exactly l blocks.
    for i1 in range(n_objects):
        for i2 in range(i1 + 1, n_objects):
            # z[j] is 1 exactly when objects i1 and i2 are both in block j
            z = [model.add_var(f"z_{i1}_{i2}_{j}", var_type=mip.BINARY) for j in range(n_blocks)]
            for j in range(n_blocks):
                model += z[j] <= matrix[i1][j]
                model += z[j] <= matrix[i2][j]
                model += z[j] >= matrix[i1][j] + matrix[i2][j] - 1
            model += mip.xsum(z) == n_blocks_per_pair

    # There is no objective: any arrangement that meets the counts is an answer.
    return model, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

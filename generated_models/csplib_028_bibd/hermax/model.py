# csplib_028_bibd: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_028_bibd.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_028_bibd.py csplib_028_bibd.json

from hermax.model import Model


def create_model(instance):
    """Balanced incomplete block design: arrange v objects into b blocks so that each
    block holds exactly k objects, each object lies in exactly r blocks, and every two
    distinct objects lie together in exactly l blocks. Reported as the v by b incidence
    matrix (rows are objects, columns are blocks)."""
    v = instance["v"]  # v: the number of objects (rows of the incidence matrix)
    b = instance["b"]  # b: the number of blocks (columns of the incidence matrix)
    r = instance["r"]  # r: how many blocks each object lies in
    k = instance["k"]  # k: how many objects each block holds
    l = instance["l"]  # l: how many blocks any two distinct objects share

    m = Model()

    # matrix[i][j] is true when object i belongs to block j
    matrix = m.bool_matrix("matrix", v, b)

    # Each object occurs in exactly r blocks: every row of the matrix has r ones.
    for i in range(v):
        m &= (sum(matrix[i][j] for j in range(b)) == r)

    # Each block contains exactly k objects: every column of the matrix has k ones.
    for j in range(b):
        m &= (sum(matrix[i][j] for i in range(v)) == k)

    # Any two distinct objects occur together in exactly l blocks. Their rows agree in
    # a block exactly when both are in it, so count, per block, the pairs of ones.
    # hermax has no product of two Booleans, so both[j] is that conjunction, posted as
    # a three-column table (a, b, both): both is true only when a and b are.
    for i1 in range(v):
        for i2 in range(i1 + 1, v):
            together = []  # together[j] is true when both objects are in block j
            for j in range(b):
                both = m.bool(f"both_{i1}_{i2}_{j}")
                m &= m.table(
                    [matrix[i1][j], matrix[i2][j], both],
                    allowed=[(False, False, False), (False, True, False),
                             (True, False, False), (True, True, True)],
                )
                together.append(both)
            m &= (sum(together) == l)

    # The design is a satisfaction problem: no objective.
    return m, {"matrix": matrix}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

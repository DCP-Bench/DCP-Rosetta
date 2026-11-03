# csplib_076_costas_arrays: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

from hermax.model import Model


def create_model(instance):
    """Costas array problem: place n marks on an n-by-n grid, one mark in each row and
    one in each column, so that the n(n-1)/2 vectors between pairs of marks are all
    different. The output costas[i] is the column (1..n) of the mark in row i."""
    # n: the grid size, which is also the number of marks (instance field "n")
    n = instance["n"]

    m = Model()

    # costas[i] is the column of the mark in row i, a value in 1..n
    costas = m.int_vector("costas", n, 1, n)

    # One mark per row and per column: the columns form a permutation.
    m &= costas.all_different()

    # Difference triangle: for each distance l = 1..n-1, the differences
    # costas[i+l] - costas[i] (i = 0..n-l-1) are the horizontal displacements of
    # the pairs of marks l rows apart. Each line of the triangle has no repeated value.
    for l in range(1, n):
        # diff_l[i] is the displacement of the pair of marks in rows i and i+l
        diff_l = m.int_vector(f"diff_{l}", n - l, -(n - 1), n - 1)
        for i in range(n - l):
            m &= (diff_l[i] == costas[i + l] - costas[i])
        # No displacement occurs twice among the pairs at distance l.
        m &= diff_l.all_different()

    # Satisfaction problem: no objective, any Costas array is an answer.
    return m, {"costas": costas}


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

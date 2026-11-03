# csplib_003_quasigroup_existence: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

from hermax.model import Model


def create_model(instance):
    """Find an order m quasigroup (an m-by-m Latin square whose entries are 0..m-1, each
    value once per row and once per column) with the QG3 property (a*b)*(b*a) = a for all
    a and b, where x*y is the entry in row x and column y. Satisfaction problem."""
    m_size = instance["m"]  # m: the order of the quasigroup, so the table is m-by-m with values 0..m-1

    m = Model()

    # table[x][y] is the value of x*y (the entry in row x, column y)
    table = m.int_matrix("table", m_size, m_size, 0, m_size - 1)

    # Latin square: every row and every column contains each value 0..m-1 exactly once.
    for i in range(m_size):
        m &= table.row(i).all_different()
        m &= table.col(i).all_different()

    # QG3 property (a*b)*(b*a) = a. hermax cannot index a matrix by a variable, so for each
    # a, b and each pair of values (p, q) we post: if a*b is p and b*a is q, then p*q is a.
    for a in range(m_size):
        for b in range(m_size):
            ab = table.row(a)[b]  # the value of a*b
            ba = table.row(b)[a]  # the value of b*a
            for p in range(m_size):
                for q in range(m_size):
                    m &= ((ab != p) | (ba != q) | (table.row(p)[q] == a))

    return m, {"quasigroup": table}


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

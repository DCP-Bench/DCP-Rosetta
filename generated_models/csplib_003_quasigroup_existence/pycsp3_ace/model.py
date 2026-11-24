# csplib_003_quasigroup_existence: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_003_quasigroup_existence.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_003_quasigroup_existence.py csplib_003_quasigroup_existence.json

from pycsp3 import *


def create_model(instance):
    """An order m quasigroup is a Latin square of size m: an m by m multiplication table in
    which each element occurs once in every row and column. The QG3.m problem asks for an
    order m quasigroup for which (a*b)*(b*a) = a for all a and b."""
    m = instance["m"]          # the order: the table is m by m, with the elements 0 to m-1
    n_cells = m * m            # the number of entries of the table

    # cells holds the table row by row as one flat array, because ACE fails (ArrayIndexOutOfBoundsException) on a matrix indexed by two variables: (a*b)*(b*a) is read at position (a*b)*m + (b*a) of cells.
    cells = VarArray(size=n_cells, dom=range(m))
    # quasigroup[i][j] is the table entry i * j, the same variable as cells[i * m + j].
    quasigroup = [[cells[i * m + j] for j in range(m)] for i in range(m)]

    # Each row of the table holds every element once.
    satisfy(AllDifferent(quasigroup[i]) for i in range(m))
    # Each column of the table holds every element once.
    satisfy(AllDifferent([quasigroup[i][j] for i in range(m)]) for j in range(m))

    # index[a][b] is where (a*b)*(b*a) sits in cells: row a*b, column b*a.
    index = VarArray(size=[m, m], dom=range(n_cells))
    satisfy(index[a][b] == quasigroup[a][b] * m + quasigroup[b][a] for a in range(m) for b in range(m))

    # The QG3 identity: the entry at position index[a][b] is a, so (a*b)*(b*a) = a.
    satisfy(cells[index[a][b]] == a for a in range(m) for b in range(m))

    return {"quasigroup": quasigroup}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("quasigroup", "=")
        for row in outputs["quasigroup"]:
            print(values(row))
    else:
        print("No solution:", status())

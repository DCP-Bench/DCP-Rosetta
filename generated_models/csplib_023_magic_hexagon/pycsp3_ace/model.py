# csplib_023_magic_hexagon: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_023_magic_hexagon.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_023_magic_hexagon.py csplib_023_magic_hexagon.json

from pycsp3 import *


def create_model(instance):
    """Arrange the numbers 1 to 19 in the cells of a hexagon, A to S, so that the sum of the numbers
    in each of the 15 lines (rows and diagonals) equals the magic constant. The cells are laid out as
    rows: A B C / D E F G / H I J K L / M N O P / Q R S."""
    magic_sum = instance["MAGIC_SUM"]  # the magic constant: every line sums to it
    n_cells = instance["NUM_CELLS"]    # the number of cells, which take the numbers 1 to n_cells

    numbers = range(1, n_cells + 1)  # the numbers placed in the cells

    A = Var(dom=numbers)  # top row, left
    B = Var(dom=numbers)  # top row, middle
    C = Var(dom=numbers)  # top row, right
    D = Var(dom=numbers)  # second row, left
    cell_E = Var(dom=numbers)  # second row, second from left (cell_E because E is reserved by PyCSP3)
    F = Var(dom=numbers)  # second row, second from right
    G = Var(dom=numbers)  # second row, right
    H = Var(dom=numbers)  # middle row, left
    I = Var(dom=numbers)  # middle row, second from left
    J = Var(dom=numbers)  # middle row, centre
    K = Var(dom=numbers)  # middle row, second from right
    L = Var(dom=numbers)  # middle row, right
    M = Var(dom=numbers)  # fourth row, left
    N = Var(dom=numbers)  # fourth row, second from left
    O = Var(dom=numbers)  # fourth row, second from right
    P = Var(dom=numbers)  # fourth row, right
    Q = Var(dom=numbers)  # bottom row, left
    R = Var(dom=numbers)  # bottom row, middle
    S = Var(dom=numbers)  # bottom row, right

    cells = [A, B, C, D, cell_E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S]

    satisfy(
        # Every cell holds a different number.
        AllDifferent(cells),
        # The five horizontal rows sum to the magic constant.
        A + B + C == magic_sum,
        D + cell_E + F + G == magic_sum,
        H + I + J + K + L == magic_sum,
        M + N + O + P == magic_sum,
        Q + R + S == magic_sum,
        # The five lines running from upper left to lower right sum to the magic constant.
        H + M + Q == magic_sum,
        D + I + N + R == magic_sum,
        A + cell_E + J + O + S == magic_sum,
        B + F + K + P == magic_sum,
        C + G + L == magic_sum,
        # The five lines running from upper right to lower left sum to the magic constant.
        A + D + H == magic_sum,
        B + cell_E + I + M == magic_sum,
        C + F + J + N + Q == magic_sum,
        G + K + O + R == magic_sum,
        L + P + S == magic_sum,
    )

    return {"LD": cells}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())

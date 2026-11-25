# csplib_023_magic_hexagon: a FOX model for GroundFOX from DCP Rosetta.
#
# A magic hexagon problem involves arranging the numbers 1 to 19 in a hexagonal pattern such
# that the sum of the numbers in each of the 15 lines (rows and diagonals) is equal to a magic
# constant, which is 38.
#
# The hexagonal grid is structured as follows: ```text A, B, C D, E, F, G H, I, J, K, L M, N,
# O, P Q, R, S ```
#
# The goal is to find an assignment of numbers to the variables A through S that satisfies all
# the sum constraints.
#
# Print the solution (LD) as a single list of 19 integers corresponding to the variables [A,
# B, ..., S].
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_023_magic_hexagon.json --check

# csplib_023_magic_hexagon: a FOX model for GroundFOX from DCP Rosetta.
#
# Place 1..N in the 19 cells A..S of a hexagon so that the 15 lines sum to MAGIC_SUM.
# Each line is a chain of nodes; reach(g, s) is the running sum through node g. The
# forward rules force the true running sums, and the last node of every line is
# restricted to MAGIC_SUM. Cells: A..S = 0..18.

FOX = """
invocabulary { Cell/1 Val/1 Node/1 Start/1 End/1 Nxt/2 CellAt/2 Sum/1 Add/3 Target/1 }
outvocabulary { LD/2 reach/2 }
theory {
    ! c [Cell(c)] : ? v [Val(v)] : LD(c, v).
    ! c [Cell(c)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~LD(c, v) | ~LD(c, w).
    ! v [Val(v)] : ! c [Cell(c)] : ! d [Cell(d) & c ~= d] : ~LD(c, v) | ~LD(d, v).
    ! g [Start(g)] : ! c [CellAt(g, c)] : ! v [Val(v)] : ~LD(c, v) | reach(g, v).
    ! g [Node(g)] : ! h [Nxt(g, h)] : ! c [CellAt(h, c)] : ! s [Sum(s)] : ! v [Val(v)] : ! t [Sum(t) & Add(s, v, t)] : ~reach(g, s) | ~LD(c, v) | reach(h, t).
    ! g [End(g)] : ! s [Sum(s) & ~Target(s)] : ~reach(g, s).
    ! g [End(g)] : ? s [Target(s)] : reach(g, s).
}
"""

# Cell indices A..S = 0..18, one list per line (order along the line does not matter).
LINES = [
    # rows
    [0, 1, 2], [3, 4, 5, 6], [7, 8, 9, 10, 11], [12, 13, 14, 15], [16, 17, 18],
    # one diagonal direction
    [7, 12, 16], [3, 8, 13, 17], [0, 4, 9, 14, 18], [1, 5, 10, 15], [2, 6, 11],
    # the other diagonal direction
    [0, 3, 7], [1, 4, 8, 12], [2, 5, 9, 13, 16], [6, 10, 14, 17], [11, 15, 18],
]


def structure(instance):
    n_cells = instance["NUM_CELLS"]
    magic = instance["MAGIC_SUM"]
    max_len = max(len(line) for line in LINES)
    max_sum = max_len * n_cells
    nodes = []  # (line index, cell) per node, in chain order
    start, end, nxt, cell_at = [], [], [], []
    for li, line in enumerate(LINES):
        first = len(nodes)
        for pos, c in enumerate(line):
            g = len(nodes)
            nodes.append((li, c))
            cell_at.append((g, c))
            if pos == 0:
                start.append(g)
            else:
                nxt.append((g - 1, g))
        end.append(len(nodes) - 1)
    add = [(s, v, s + v) for s in range(max_sum + 1) for v in range(1, n_cells + 1)
           if s + v <= max_sum]
    return {
        "Cell": list(range(n_cells)),
        "Val": list(range(1, n_cells + 1)),
        "Node": list(range(len(nodes))),
        "Start": start,
        "End": end,
        "Nxt": nxt,
        "CellAt": cell_at,
        "Sum": list(range(max_sum + 1)),
        "Add": add,
        "Target": [magic] if magic <= max_sum else [],
    }

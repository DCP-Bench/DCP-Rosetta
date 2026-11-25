# csplib_057_killer_sudoku: a FOX model for GroundFOX from DCP Rosetta.
#
# Killer sudoku (also killer su doku, sumdoku, sum doku, addoku, or samunamupure) is a puzzle
# that combines elements of sudoku and kakuro. Despite the name, the simpler killer sudokus
# can be easier to solve than regular sudokus, depending on the solver's skill at mental
# arithmetic; the hardest ones, however, can take hours to crack.
#
# The objective is to fill the grid with numbers from 1 to 9 in a way that the following
# conditions are met:
#
# * Each row, column, and nonet contains each number exactly once. * The sum of all numbers in
# a cage must match the small number printed in its corner. * No number appears more than once
# in a cage. (This is the standard rule for killer sudokus, and implies that no cage can
# include more than 9 cells.)
#
# Print the solution matrix (x) as a list of lists of integers ranging from 1 to 9.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_057_killer_sudoku.json --check

from math import isqrt

MAX_CELLS = 9      # a killer cage has at most nine cells (distinct digits 1..9)
MAX_SUM = 45       # 1 + 2 + ... + 9


def _build_fox():
    K = MAX_CELLS
    inputs = ["Idx/1", "Val/1", "Num/1", "Succ/2", "Add/3", "Peer/4", "Cage/1", "Sum/2"]
    inputs += ["Slot%d/3" % k for k in range(1, K + 1)]
    inputs += ["Last%d/1" % k for k in range(1, K + 1)]
    outs = ["x/3"]
    outs += ["P%d/2" % k for k in range(1, K + 1)]
    outs += ["Q%d/2" % k for k in range(1, K + 1)]
    lines = ["invocabulary { " + " ".join(inputs) + " }",
             "outvocabulary { " + " ".join(outs) + " }",
             "theory {",
             "    ! r [Idx(r)] : ! c [Idx(c)] : ? v [Val(v)] : x(r, c, v).",
             "    ! r [Idx(r)] : ! c [Idx(c)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~x(r, c, v) | ~x(r, c, w).",
             "    ! r1 [Idx(r1)] : ! c1 [Idx(c1)] : ! r2 [Idx(r2)] : ! c2 [Idx(c2) & Peer(r1, c1, r2, c2)] : "
             "! v [Val(v)] : ~x(r1, c1, v) | ~x(r2, c2, v)."]
    # digits are distinct inside a cage: cells at different slots of one cage
    for i in range(1, K + 1):
        for j in range(i + 1, K + 1):
            lines.append("    ! g [Cage(g)] : ! r1 [Idx(r1)] : ! c1 [Slot%d(g, r1, c1)] : "
                         "! r2 [Idx(r2)] : ! c2 [Slot%d(g, r2, c2)] : ! v [Val(v)] : "
                         "~x(r1, c1, v) | ~x(r2, c2, v)." % (i, j))
    # running sum of the first k cells of each cage: P_k(g, s), kept at most one per cage
    for k in range(1, K + 1):
        if k == 1:
            lines.append("    ! g [Cage(g)] : ! r [Idx(r)] : ! c [Slot1(g, r, c)] : ! v [Val(v)] : "
                         "~x(r, c, v) | P1(g, v).")
        else:
            lines.append("    ! g [Cage(g)] : ! s [Num(s)] : ! v [Val(v)] : ! t [Add(s, v, t)] : "
                         "! r [Idx(r)] : ! c [Slot%d(g, r, c)] : "
                         "~P%d(g, s) | ~x(r, c, v) | P%d(g, t)." % (k, k - 1, k))
        lines.append("    ! g [Cage(g)] : ! s [Num(s)] : ~P%d(g, s) | Q%d(g, s)." % (k, k))
        lines.append("    ! g [Cage(g)] : ! s [Num(s)] : ! t [Succ(s, t)] : ~Q%d(g, s) | Q%d(g, t)." % (k, k))
        lines.append("    ! g [Cage(g)] : ! s [Num(s)] : ! t [Succ(s, t)] : ~Q%d(g, s) | ~P%d(g, t)." % (k, k))
        # a cage with exactly k cells has its sum at slot k
        lines.append("    ! g [Last%d(g)] : ! s [Sum(g, s)] : P%d(g, s)." % (k, k))
    lines.append("}")
    return "\n".join(lines) + "\n"


FOX = _build_fox()


def _is_cell(x):
    return isinstance(x, list) and len(x) == 2 and all(isinstance(t, int) and not isinstance(t, bool) for t in x)


def _cells_in(x):
    if _is_cell(x):
        return [(x[0], x[1])]
    if isinstance(x, list):
        return [rc for y in x for rc in _cells_in(y)]
    return []


def _parse_cages(problem):
    """A cage is a list holding its cells (two-element int lists) and its int sum, in either order."""
    cages = []

    def walk(x):
        if _is_cell(x) or not isinstance(x, list):
            return
        sums = [y for y in x if isinstance(y, int) and not isinstance(y, bool)]
        has_cells = any(isinstance(y, list) for y in x)
        if sums and has_cells:
            cells = [rc for y in x if isinstance(y, list) for rc in _cells_in(y)]
            cages.append((cells, sums[0]))
            return
        for y in x:
            walk(y)

    walk(problem)
    return cages


def structure(instance):
    n = instance["n"]
    box = isqrt(n)
    cages = _parse_cages(instance["problem"])
    coords = [rc for cells, _s in cages for rc in cells]
    base = 0 if not coords or min(min(r, c) for r, c in coords) == 0 else 1
    cages = [([(r - base, c - base) for r, c in cells], s) for cells, s in cages]

    peers = []
    for r1 in range(n):
        for c1 in range(n):
            for r2 in range(n):
                for c2 in range(n):
                    if (r1, c1) == (r2, c2):
                        continue
                    same_box = (r1 // box == r2 // box) and (c1 // box == c2 // box)
                    if r1 == r2 or c1 == c2 or same_box:
                        peers.append((r1, c1, r2, c2))

    out = {
        "Idx": range(n),
        "Val": range(1, n + 1),
        "Num": range(0, MAX_SUM + 1),
        "Succ": [(s, s + 1) for s in range(0, MAX_SUM)],
        "Add": [(s, v, s + v) for s in range(0, MAX_SUM + 1) for v in range(1, n + 1) if s + v <= MAX_SUM],
        "Peer": peers,
        "Cage": list(range(len(cages))),
        "Sum": [(g, s) for g, (_cells, s) in enumerate(cages)],
    }
    for k in range(1, MAX_CELLS + 1):
        out["Slot%d" % k] = [(g, cells[k - 1][0], cells[k - 1][1])
                             for g, (cells, _s) in enumerate(cages) if len(cells) >= k]
        out["Last%d" % k] = [g for g, (cells, _s) in enumerate(cages) if len(cells) == k]
    return out

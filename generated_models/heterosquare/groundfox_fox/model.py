# heterosquare: a FOX model for GroundFOX from DCP Rosetta.
#
# A heterosquare of order n is an n by n square whose elements are distinct integers from 1 to
# n^2 such that the sums of the rows, columns and diagonals are all different. Here is an
# example of heterosquare of order 3
#
# ```text 19
#
# 1 2 3 6 8 9 4 21 7 6 5 18
#
# 16 17 12 15 (Sums) ```
#
# Print a heterosquare (x) of a given order as a list of lists of integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py heterosquare.json --check

# heterosquare: a FOX model for GroundFOX from DCP Rosetta.
#
# An n x n square with the values 1..n^2 each used once, such that the 2n+2 line sums
# (rows, columns, two diagonals) are pairwise distinct. Partial line sums are tracked by a
# state chain per line; the chain positions and cells of each line are data in the structure.
# Output x[r][c] is the value of cell (r, c).
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Row/1 Col/1 Val/1 Line/1 Lvl/1 Pos/1 Next/2 Last/1 Sum/1 Add/3 LCell/4 }
outvocabulary { x/3 st/3 }
theory {
    ! r [Row(r)] : ! c [Col(c)] : ? v [Val(v)] : x(r,c,v).
    ! r [Row(r)] : ! c [Col(c)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~x(r,c,v) | ~x(r,c,w).
    ! v [Val(v)] : ! r [Row(r)] : ! c [Col(c)] : ! d [Col(d) & c ~= d] : ~x(r,c,v) | ~x(r,d,v).
    ! v [Val(v)] : ! r [Row(r)] : ! s [Row(s) & r ~= s] : ! c [Col(c)] : ! d [Col(d)] : ~x(r,c,v) | ~x(s,d,v).
    ! L [Line(L)] : st(L,0,0).
    ! L [Line(L)] : ! j [Lvl(j)] : ? s [Sum(s)] : st(L,j,s).
    ! L [Line(L)] : ! j [Lvl(j)] : ! s [Sum(s)] : ! t [Sum(t) & s ~= t] : ~st(L,j,s) | ~st(L,j,t).
    ! L [Line(L)] : ! j [Pos(j)] : ! jp [Next(j,jp)] : ! r : ! c [LCell(L,j,r,c)] : ! s [Sum(s)] : ! v [Val(v)] : ! t [Add(s,v,t)] : ~st(L,j,s) | ~x(r,c,v) | st(L,jp,t).
    ! L [Line(L)] : ! M [Line(M) & L ~= M] : ! j [Last(j)] : ! s [Sum(s)] : ~st(L,j,s) | ~st(M,j,s).
}
"""


def structure(instance):
    n = instance["n"]
    n2 = n * n
    ns = n ** 3
    lines = []
    for r in range(n):
        lines.append([(r, c) for c in range(n)])
    for c in range(n):
        lines.append([(r, c) for r in range(n)])
    lines.append([(j, j) for j in range(n)])
    lines.append([(j, n - 1 - j) for j in range(n)])
    lcell = [(L, j, r, c) for L, cells in enumerate(lines) for j, (r, c) in enumerate(cells)]
    add = [(s, v, s + v) for s in range(ns + 1) for v in range(1, n2 + 1) if s + v <= ns]
    dom = set(range(max(ns, n2, 2 * n + 2, n + 1) + 1))
    return {
        "domain": sorted(dom),
        "Row": list(range(n)),
        "Col": list(range(n)),
        "Val": list(range(1, n2 + 1)),
        "Line": list(range(2 * n + 2)),
        "Lvl": list(range(n + 1)),
        "Pos": list(range(n)),
        "Next": [(j, j + 1) for j in range(n)],
        "Last": [n],
        "Sum": list(range(ns + 1)),
        "Add": add,
        "LCell": lcell,
    }

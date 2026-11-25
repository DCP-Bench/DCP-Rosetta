# futoshiki: a FOX model for GroundFOX from DCP Rosetta.
#
# The futoshiki puzzle is played on a square grid, such as 5 x 5. The objective is to place
# the numbers 1 to 5 (or whatever the dimensions are) such that each row, and column contains
# each of the digits 1 to 5. Some digits may be given at the start. In addition, inequality
# constraints are also initially specified between some of the squares, such that one must be
# higher or lower than its neighbour. These constraints must be honoured as the grid is filled
# out.
#
# Print the completed grid (grid) that satisfies the above conditions as a list of lists of
# integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py futoshiki.json --check

FOX = """
invocabulary { Row/1 Col/1 Val/1 Less/2 Giv/3 Ineq/4 }
outvocabulary { grid/3 }
theory {
    ! r [Row(r)] : ! c [Col(c)] : ? v [Val(v)] : grid(r, c, v).
    ! r [Row(r)] : ! c [Col(c)] : ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~grid(r, c, v) | ~grid(r, c, w).
    ! r [Row(r)] : ! v [Val(v)] : ! c [Col(c)] : ! d [Col(d) & ~(c = d)] : ~grid(r, c, v) | ~grid(r, d, v).
    ! c [Col(c)] : ! v [Val(v)] : ! r [Row(r)] : ! s [Row(s) & ~(r = s)] : ~grid(r, c, v) | ~grid(s, c, v).

    ! r [Row(r)] : ! c [Col(c)] : ! v [Giv(r, c, v)] : grid(r, c, v).

    ! r1 [Row(r1)] : ! c1 [Col(c1)] : ! r2 [Row(r2)] : ! c2 [Col(c2) & Ineq(r1, c1, r2, c2)] : ! a [Val(a)] : ! b [Val(b) & ~Less(a, b)] : ~grid(r1, c1, a) | ~grid(r2, c2, b).
}
"""


def structure(instance):
    values = instance["values"]
    n = len(values)
    return {
        "Row": list(range(n)),
        "Col": list(range(n)),
        "Val": list(range(1, n + 1)),
        "Less": [(a, b) for a in range(1, n + 1) for b in range(1, n + 1) if a < b],
        "Giv": [(r, c, values[r][c]) for r in range(n) for c in range(n) if values[r][c] != 0],
        "Ineq": [tuple(x - 1 for x in row) for row in instance["lt"]],
    }

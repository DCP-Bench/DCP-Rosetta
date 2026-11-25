# discrete_tomography: a FOX model for GroundFOX from DCP Rosetta.
#
# This is a little "tomography" problem, taken from an old issue of Scientific American.
#
# A matrix which contains zeroes and ones gets "x-rayed" vertically and horizontally, giving
# the total number of ones in each row and column. The problem is to reconstruct the contents
# of the matrix from this information.
#
# Print the solution matrix with 0 and 1 (matrix) as a list of lists.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py discrete_tomography.json --check

# discrete_tomography: a FOX model for GroundFOX from DCP Rosetta.
#
# A 0/1 matrix with given row sums and column sums. Output matrix[i][j] is 0 or 1.
#
# Encoding: for each row an exact sequential counter E(i, p, c) over the columns p,
# and for each column an exact counter F(j, p, c) over the rows p; each counter's
# final state is tied to the given sum by data relations RowS / ColS.

FOX = """
invocabulary { RowI/1 ColI/1 NextC/2 StartC/1 LastC/1 NextR/2 StartR/1 LastR/1
               Cnt/1 Ge2/1 Prev/2 RowS/2 ColS/2 }
outvocabulary { matrix/3 E/3 F/3 }
theory {
    ! i [RowI(i)] : ! j [ColI(j)] : matrix(i, j, 0) | matrix(i, j, 1).
    ! i [RowI(i)] : ! j [ColI(j)] : ~matrix(i, j, 0) | ~matrix(i, j, 1).

    ! i [RowI(i)] : ! p [ColI(p)] : ~E(i, p, 0) | ~matrix(i, p, 1).
    ! j [ColI(j)] : ! p [RowI(p)] : ~F(j, p, 0) | ~matrix(p, j, 1).
    ! i [RowI(i)] : ! s [StartC(s)] : ~E(i, s, 0) | matrix(i, s, 0).
    ! i [RowI(i)] : ! s [StartC(s)] : ~E(i, s, 1) | matrix(i, s, 1).
    ! i [RowI(i)] : ! s [StartC(s)] : ! c [Ge2(c)] : ~E(i, s, c).
    ! i [RowI(i)] : ! p [ColI(p)] : ! q [NextC(q, p)] : ! c [Cnt(c)] : ! b [Prev(b, c)] : ~E(i, p, c) | ~matrix(i, p, 1) | E(i, q, b).
    ! i [RowI(i)] : ! p [ColI(p)] : ! q [NextC(q, p)] : ! c [Cnt(c)] : ~E(i, p, c) | matrix(i, p, 1) | E(i, q, c).
    ! i [RowI(i)] : ! l [LastC(l)] : ! r [RowS(i, r)] : E(i, l, r).

    ! j [ColI(j)] : ! s [StartR(s)] : ~F(j, s, 0) | matrix(s, j, 0).
    ! j [ColI(j)] : ! s [StartR(s)] : ~F(j, s, 1) | matrix(s, j, 1).
    ! j [ColI(j)] : ! s [StartR(s)] : ! c [Ge2(c)] : ~F(j, s, c).
    ! j [ColI(j)] : ! p [RowI(p)] : ! q [NextR(q, p)] : ! c [Cnt(c)] : ! b [Prev(b, c)] : ~F(j, p, c) | ~matrix(p, j, 1) | F(j, q, b).
    ! j [ColI(j)] : ! p [RowI(p)] : ! q [NextR(q, p)] : ! c [Cnt(c)] : ~F(j, p, c) | matrix(p, j, 1) | F(j, q, c).
    ! j [ColI(j)] : ! l [LastR(l)] : ! r [ColS(j, r)] : F(j, l, r).
}
"""


def structure(instance):
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    nr, nc = len(row_sums), len(col_sums)
    top = max([nr, nc] + list(row_sums) + list(col_sums))
    counts = list(range(top + 1))
    return {
        "domain": counts,
        "RowI": list(range(nr)),
        "ColI": list(range(nc)),
        "NextC": [(q, q + 1) for q in range(nc - 1)],
        "StartC": [0],
        "LastC": [nc - 1],
        "NextR": [(q, q + 1) for q in range(nr - 1)],
        "StartR": [0],
        "LastR": [nr - 1],
        "Cnt": counts,
        "Ge2": list(range(2, top + 1)),
        "Prev": [(c - 1, c) for c in range(1, top + 1)],
        "RowS": [(i, row_sums[i]) for i in range(nr)],
        "ColS": [(j, col_sums[j]) for j in range(nc)],
    }

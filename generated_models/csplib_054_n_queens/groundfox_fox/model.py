# csplib_054_n_queens: a FOX model for GroundFOX from DCP Rosetta.
#
# Can \( n \) queens (of the same color) be placed on a \( n \times n \) chessboard so that
# none of the queens can attack each other? In chess, a queen attacks other squares on the
# same row, column, or either diagonal as itself. So the \( n \)-queens problem is to find a
# set of \( n \) locations on a chessboard, no two of which are on the same row, column or
# diagonal.
#
# Print the positions of the queens on the chessboard (queens) as a list of n integers -
# ranging from 1 to n, where the i-th integer represents the column position of the queen in
# the i-th row.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_054_n_queens.json --check

FOX = """
invocabulary { Row/1 Val/1 Diag/4 }
outvocabulary { queens/2 }
theory {
    ! i [Row(i)] : ? v [Val(v)] : queens(i, v).
    ! i [Row(i)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~queens(i, v) | ~queens(i, w).
    ! v [Val(v)] : ! i [Row(i)] : ! j [Row(j) & i ~= j] : ~queens(i, v) | ~queens(j, v).
    ! i [Row(i)] : ! v [Val(v)] : ! j [Row(j)] : ! w [Val(w)] : ~queens(i, v) | ~queens(j, w) | ~Diag(i, v, j, w).
}
"""


def structure(instance):
    n = instance["n"]
    rows = list(range(n))
    vals = list(range(1, n + 1))
    # Pairs of squares on one diagonal (rows i < j, columns v, w with |v - w| = j - i).
    diag = [(i, v, j, w) for i in rows for j in rows if i < j
            for v in vals for w in vals if abs(v - w) == j - i]
    return {
        "domain": list(range(n + 1)),
        "Row": rows,
        "Val": vals,
        "Diag": diag,
    }

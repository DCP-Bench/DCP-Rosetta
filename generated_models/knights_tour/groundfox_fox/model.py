# knights_tour: a FOX model for GroundFOX from DCP Rosetta.
#
# A knight's tour is a sequence of moves of a knight on a chessboard such that the knight
# visits every square exactly once (without returning to the starting square). The objective
# is to find a knight's tour on a chessboard. The tour is represented by integers from 0 to
# `n*n-1`, where n is the size of the chessboard.
#
# Print the chessboard (x) as a list of lists of integers from 0 to `n*n-1`, where each
# integer represents the move number of the knight.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/knights_tour.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py knights_tour.json --check

FOX = """
invocabulary { Row/1 Col/1 Val/1 Next/2 KN/4 }
outvocabulary { x/3 Rk/2 }
theory {
    ! r [Row(r)] : ! c [Col(c)] : ? k [Val(k)] : x(r, c, k).
    ! r [Row(r)] : ! c [Col(c)] : ! k [Val(k)] : ! j [Val(j) & k ~= j] : ~x(r, c, k) | ~x(r, c, j).
    ! k [Val(k)] : ? r [Row(r)] : Rk(r, k).
    ! k [Val(k)] : ! r [Row(r)] : ? c [Col(c)] : x(r, c, k) | ~Rk(r, k).
    ! k [Val(k)] : ! r [Row(r)] : ! c [Col(c)] : ! s [Row(s)] : ! t [Col(t) & (r ~= s | c ~= t)] : ~x(r, c, k) | ~x(s, t, k).
    ! k : ! j [Next(k, j)] : ! r [Row(r)] : ! c [Col(c)] : ? s [Row(s)] : ? t [KN(r, c, s, t)] : x(s, t, j) | ~x(r, c, k).
    ! j [Val(j)] : ! k [Next(k, j)] : ! s [Row(s)] : ! t [Col(t)] : ? r [Row(r)] : ? c [KN(r, c, s, t)] : x(r, c, k) | ~x(s, t, j).
}
"""

FLAGS = []


def structure(instance):
    n = instance["n"]
    moves = [(1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)]
    kn = [(r, c, r + dr, c + dc)
          for r in range(n) for c in range(n) for dr, dc in moves
          if 0 <= r + dr < n and 0 <= c + dc < n]
    cells = n * n
    return {
        "domain": range(cells),
        "Row": range(n),
        "Col": range(n),
        "Val": range(cells),
        "Next": [(k, k + 1) for k in range(cells - 1)],
        "KN": kn,
    }

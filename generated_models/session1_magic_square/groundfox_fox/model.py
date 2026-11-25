# session1_magic_square: a FOX model for GroundFOX from DCP Rosetta.
#
# A magic square is an n x n grid (n != 2) such that each cell contains a different integer
# from 1 to n^2 and the sum of the integers in each row, column and diagonal is equal. Find a
# magic square for a given size n, knowing that the sum of integers of each row, column and
# diagonal has to be equal to n(n^2+ 1)/2 (integer).
#
# Print the magic square as a list of lists (square) of integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session1_magic_square.json --check

# session1_magic_square: a FOX model for GroundFOX from DCP Rosetta.
#
# An n x n magic square using each of 1..n^2 once, with every row, column and both
# diagonals summing to n(n^2+1)/2. Output the square (square[i][j]).

FOX = """
invocabulary { Idx/1 Val/1 Diff/4 Sum/1 Dead/1 Bad/1 Pref/1 Start/1 Last/1 Next/2 Add/3 Line/1 LC/4 }
outvocabulary { square/3 Acc/3 }
theory {
    ! i [Idx(i)] : ! j [Idx(j)] : ? v [Val(v)] : square(i, j, v).
    ! i [Idx(i)] : ! j [Idx(j)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~square(i, j, v) | ~square(i, j, w).
    ! v [Val(v)] : ! i [Idx(i)] : ! j [Idx(j)] : ! k [Idx(k)] : ! l [Diff(i, j, k, l)] : ~square(i, j, v) | ~square(k, l, v).
    ! l [Line(l)] : ! p [Start(p)] : ! s [Start(s)] : Acc(l, p, s).
    ! l [Line(l)] : ! p [Pref(p)] : ! i [Idx(i)] : ! j [LC(l, p, i, j)] : ! s [Sum(s)] : ! v [Val(v)] : ! t [Add(s, v, t)] : ! q [Next(p, q)] : ~Acc(l, p, s) | ~square(i, j, v) | Acc(l, q, t).
    ! l [Line(l)] : ! p [Pref(p)] : ! d [Dead(d)] : ~Acc(l, p, d).
    ! l [Line(l)] : ! p [Last(p)] : ! s [Bad(s)] : ~Acc(l, p, s).
}
"""


def structure(instance):
    n = instance["n"]
    S = n * (n * n + 1) // 2
    cells = [(i, j) for i in range(n) for j in range(n)]
    # LC(line, position, row, col): the cell at each position of each line.
    lc = []
    for r in range(n):
        for p in range(n):
            lc.append((r, p, r, p))
    for c in range(n):
        for p in range(n):
            lc.append((n + c, p, p, c))
    for p in range(n):
        lc.append((2 * n, p, p, p))
        lc.append((2 * n + 1, p, p, n - 1 - p))
    # Partial sums: a running sum above S is clamped to the dead element S+1.
    add = [(s, v, min(s + v, S + 1)) for s in range(S + 1) for v in range(1, n * n + 1)]
    return {
        "Idx": range(n),
        "Val": range(1, n * n + 1),
        "Diff": [(i, j, k, l) for (i, j) in cells for (k, l) in cells if (i, j) != (k, l)],
        "Sum": range(S + 2),
        "Dead": [S + 1],
        "Bad": [s for s in range(S + 2) if s != S],
        "Pref": range(n + 1),
        "Start": [0],
        "Last": [n],
        "Next": [(p, p + 1) for p in range(n)],
        "Add": add,
        "Line": range(2 * n + 2),
        "LC": lc,
    }

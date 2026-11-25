# calvin_puzzle: a FOX model for GroundFOX from DCP Rosetta.
#
# The Purpose of the Game
#
# To take an n by n grid, representing n^2 squares, and completely fill every square with the
# numbers 1 to n^2 in sequence, each used once, starting from any square, based on two types
# of movements.
#
# Movement Type I) If the next number in the sequence is going to be placed vertically or
# horizontally, then it must be placed exactly three squares away from the previous number
# (there must be a two square gap between the numbers).
#
# Movement Type II) If the next number in the sequence is going to be placed diagonally, then
# it must be placed exactly two squares away from the previous number (there must be a one
# square gap between the numbers).
#
# Print the completed grid (x) as a list of lists of integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py calvin_puzzle.json --check

# calvin_puzzle: a FOX model for GroundFOX from DCP Rosetta.
#
# x(i, j, v) is true iff cell (i, j) holds the number v (1..n*n). Each number occurs in
# at most one cell (N cells with distinct numbers in 1..N is a bijection, so no existential
# over cells is needed for values; a nested existential is rejected by the proof check). The move from v to v+1 is a
# Type I or Type II knight-like step, computed as the data relation Move(i, j, k, l).
# Mv(i, j) marks the cells that have at least one outgoing move; the others cannot hold a
# number that has a successor.

FOX = """
invocabulary { Idx/1 Val/1 Succ/2 Move/4 Mv/2 }
outvocabulary { x/3 }
theory {
    ! i [Idx(i)] : ! j [Idx(j)] : ? v [Val(v)] : x(i, j, v).
    ! i [Idx(i)] : ! j [Idx(j)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~x(i, j, v) | ~x(i, j, w).
    ! v [Val(v)] : ! i [Idx(i)] : ! j [Idx(j)] : ! k [Idx(k) & i ~= k] : ! l [Idx(l)] : ~x(i, j, v) | ~x(k, l, v).
    ! v [Val(v)] : ! i [Idx(i)] : ! j [Idx(j)] : ! l [Idx(l) & j ~= l] : ~x(i, j, v) | ~x(i, l, v).
    ! i [Idx(i)] : ! j [Mv(i, j)] : ! v [Val(v)] : ! w [Succ(v, w)] : ? k [Idx(k)] : ? l [Move(i, j, k, l)] : x(k, l, w) | ~x(i, j, v).
    ! i [Idx(i)] : ! j [Idx(j) & ~Mv(i, j)] : ! v [Val(v)] : ! w [Succ(v, w)] : ~x(i, j, v).
}
"""


def structure(instance):
    n = instance["n"]
    N = n * n
    # Type I: exactly three squares apart horizontally or vertically.
    # Type II: exactly two squares apart diagonally.
    steps = {(0, 3), (3, 0), (2, 2)}
    moves = [(i, j, k, l)
             for i in range(n) for j in range(n) for k in range(n) for l in range(n)
             if (abs(i - k), abs(j - l)) in steps]
    has_move = sorted({(i, j) for i, j, _, _ in moves})
    return {
        "Idx": range(n),
        "Val": range(1, N + 1),
        "Succ": [(v, v + 1) for v in range(1, N)],
        "Move": moves,
        "Mv": has_move,
    }

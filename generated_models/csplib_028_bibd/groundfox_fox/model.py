# csplib_028_bibd: a FOX model for GroundFOX from DCP Rosetta.
#
# Balanced Incomplete Block Design (BIBD) generation is a standard combinatorial problem from
# design theory, originally used in the design of statistical experiments but since finding
# other applications such as cryptography. It is a special case of Block Design, which also
# includes Latin Square problems.
#
# A BIBD is defined as an arrangement of \( v \) distinct objects into \( b \) blocks such
# that each block contains exactly \( k \) distinct objects, each object occurs in exactly \(
# r \) different blocks, and every two distinct objects occur together in exactly \( \lambda
# \) blocks. Another way of defining a BIBD is in terms of its incidence matrix, which is a \(
# v \) by \( b \) binary matrix with exactly \( r \) ones per row, \( k \) ones per column,
# and with a scalar product of \( \lambda \) between any pair of distinct rows. A BIBD is
# therefore specified by its parameters \( (v, b, r, k, \lambda) \). An example of a solution
# for \( (7, 7, 3, 3, 1) \) is:
#
# ```text 0 1 1 0 0 1 0 1 0 1 0 1 0 0 0 0 1 1 0 0 1 1 1 0 0 0 0 1 0 0 0 0 1 1 1 1 0 0 1 0 1 0
# 0 1 0 1 1 0 0 ```
#
# Print the incidence matrix of the BIBD (matrix) as a list of lists of integers - 0s and 1s.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_028_bibd.json --check

# csplib_028_bibd: a FOX model for GroundFOX from DCP Rosetta.

FOX = """
invocabulary { Row/1 Col/1 NxtR/2 NxtC/2 RLast/1 CLast/1 Pair/2 Count/1 Succ/2 Bit/1 TR/1 TK/1 TL/1 }
outvocabulary { matrix/3 rc/3 cc/3 dc/4 }
theory {
    ! i [Row(i)] : ! j [Col(j)] : ? x [Bit(x)] : matrix(i, j, x).
    ! i [Row(i)] : ! j [Col(j)] : ! x [Bit(x)] : ! y [Bit(y) & x ~= y] : ~matrix(i, j, x) | ~matrix(i, j, y).
    ! i [Row(i)] : rc(i, 0, 0).
    ! i [Row(i)] : ! p [Col(p)] : ! q [NxtC(p, q)] : ! t [Count(t)] : ! u [Succ(t, u)] : ~rc(i, p, t) | ~matrix(i, p, 1) | rc(i, q, u).
    ! i [Row(i)] : ! p [Col(p)] : ! q [NxtC(p, q)] : ! t [Count(t)] : ~rc(i, p, t) | matrix(i, p, 1) | rc(i, q, t).
    ! i [Row(i)] : ! e [CLast(e)] : ! t [Count(t) & ~TR(t)] : ~rc(i, e, t).
    ! j [Col(j)] : cc(j, 0, 0).
    ! j [Col(j)] : ! p [Row(p)] : ! q [NxtR(p, q)] : ! t [Count(t)] : ! u [Succ(t, u)] : ~cc(j, p, t) | ~matrix(p, j, 1) | cc(j, q, u).
    ! j [Col(j)] : ! p [Row(p)] : ! q [NxtR(p, q)] : ! t [Count(t)] : ~cc(j, p, t) | matrix(p, j, 1) | cc(j, q, t).
    ! j [Col(j)] : ! e [RLast(e)] : ! t [Count(t) & ~TK(t)] : ~cc(j, e, t).
    ! a [Row(a)] : ! b [Pair(a, b)] : dc(a, b, 0, 0).
    ! a [Row(a)] : ! b [Pair(a, b)] : ! p [Col(p)] : ! q [NxtC(p, q)] : ! t [Count(t)] : ! u [Succ(t, u)] : ~dc(a, b, p, t) | ~matrix(a, p, 1) | ~matrix(b, p, 1) | dc(a, b, q, u).
    ! a [Row(a)] : ! b [Pair(a, b)] : ! p [Col(p)] : ! q [NxtC(p, q)] : ! t [Count(t)] : ~dc(a, b, p, t) | matrix(a, p, 1) | dc(a, b, q, t).
    ! a [Row(a)] : ! b [Pair(a, b)] : ! p [Col(p)] : ! q [NxtC(p, q)] : ! t [Count(t)] : ~dc(a, b, p, t) | matrix(b, p, 1) | dc(a, b, q, t).
    ! a [Row(a)] : ! b [Pair(a, b)] : ! e [CLast(e)] : ! t [Count(t) & ~TL(t)] : ~dc(a, b, e, t).
}
"""


def structure(instance):
    v, b = instance["v"], instance["b"]
    r, k, l = instance["r"], instance["k"], instance["l"]
    M = max(v, b) + 1
    return {
        "Row": range(v),
        "Col": range(b),
        "NxtR": [(p, p + 1) for p in range(v)],
        "NxtC": [(p, p + 1) for p in range(b)],
        "RLast": [v],
        "CLast": [b],
        "Pair": [(a, c) for a in range(v) for c in range(a + 1, v)],
        "Count": range(M),
        "Succ": [(t, t + 1) for t in range(M - 1)],
        "Bit": [0, 1],
        "TR": [r],
        "TK": [k],
        "TL": [l],
    }

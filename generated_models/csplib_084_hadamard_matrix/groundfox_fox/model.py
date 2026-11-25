# csplib_084_hadamard_matrix: a FOX model for GroundFOX from DCP Rosetta.
#
# For every odd positive integer \( \ell \) (and \( m = \frac{\ell - 1}{2} \)) we define the
# 2cc Hadamard matrix Legendre pairs CSP using the \{V, D, C\} format (Variables, Domains,
# Constraints) as follows:
#
# - \( V = \{a_1, \ldots, a_\ell, b_1, \ldots, b_\ell\} \), a set of \( 2 \cdot \ell \)
# variables - \( D = \{D_{a_1}, \ldots, D_{a_\ell}, D_{b_1}, \ldots, D_{b_\ell}\} \), a set of
# \( 2 \cdot \ell \) domains, all of them equal to \{-1, +1\} - \( C = \{c_1, \ldots, c_m,
# c_{m+1}, c_{m+2}\} \), a set of \( m+2 \) constraints (\( m \) quadratic constraints and 2
# linear constraints)
#
# The \( m \) quadratic constraints are given by: \[ c_s := \text{PAF}(A, s) + \text{PAF}(B,
# s) = -2, \forall s = 1, \ldots, m \] where PAF denotes the periodic autocorrelation
# function: (\(i + s\) is taken mod \( \ell \) when it exceeds \( \ell \)) \[ A = [a_1,
# \ldots, a_\ell], \, \text{PAF}(A, s) = \sum_{i=1}^\ell a_i a_{i+s} \] \[ B = [b_1, \ldots,
# b_\ell], \, \text{PAF}(B, s) = \sum_{i=1}^\ell b_i b_{i+s} \]
#
# The 2 linear constraints are given by: \[ c_{m+1} := a_1 + \ldots + a_\ell = 1 \] \[ c_{m+2}
# := b_1 + \ldots + b_\ell = 1 \]
#
# Print the variables a and b (a, b) as lists of l integers, with values either -1 or 1.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_084_hadamard_matrix.json --check

# csplib_084_hadamard_matrix: a GroundFOX model of Legendre pairs of odd length l.
# a(i, v), b(i, v): the two sequences, with values -1 (element neg1) and +1 (element 1).
# Bit(g, i) is true when entry i of sequence g is +1. Eq(g, s, i) holds when the entries at
# i and (i+s) mod l of sequence g agree. The periodic autocorrelations sum to -2 for every
# shift s exactly when the number of agreeing pairs over both sequences is l - 1.
# Counting uses forward-forced chains; the number of +1 entries must be (l + 1) / 2.

FOX = """
invocabulary { Pos/1 Seq/1 Sgn/1 Shift/1 Pr/3 St/1 Nxt/2 Itm/3 Cnt/1 Inc/2 Tgt/1 Hlf/1 Mid/1 Lst/1 }
outvocabulary { a/2 b/2 Bit/2 Eq/3 C/3 D/3 }
theory {
    ! i [Pos(i)] : ? v [Sgn(v)] : a(i, v).
    ! i [Pos(i)] : ! v [Sgn(v)] : ! w [Sgn(w) & v ~= w] : ~a(i, v) | ~a(i, w).
    ! i [Pos(i)] : ? v [Sgn(v)] : b(i, v).
    ! i [Pos(i)] : ! v [Sgn(v)] : ! w [Sgn(w) & v ~= w] : ~b(i, v) | ~b(i, w).

    ! i [Pos(i)] : ~Bit(0, i) | a(i, 1).
    ! i [Pos(i)] : Bit(0, i) | ~a(i, 1).
    ! i [Pos(i)] : ~Bit(1, i) | b(i, 1).
    ! i [Pos(i)] : Bit(1, i) | ~b(i, 1).

    ! s [Shift(s)] : ! g [Seq(g)] : ! i [Pos(i)] : ! j [Pr(s, i, j)] : ~Bit(g, i) | ~Bit(g, j) | Eq(g, s, i).
    ! s [Shift(s)] : ! g [Seq(g)] : ! i [Pos(i)] : ! j [Pr(s, i, j)] : Bit(g, i) | Bit(g, j) | Eq(g, s, i).
    ! s [Shift(s)] : ! g [Seq(g)] : ! i [Pos(i)] : ! j [Pr(s, i, j)] : ~Eq(g, s, i) | ~Bit(g, i) | Bit(g, j).
    ! s [Shift(s)] : ! g [Seq(g)] : ! i [Pos(i)] : ! j [Pr(s, i, j)] : ~Eq(g, s, i) | Bit(g, i) | ~Bit(g, j).

    ! s [Shift(s)] : C(s, 0, 0).
    ! s [Shift(s)] : ! st [St(st)] : ! st2 [Nxt(st, st2)] : ! g [Seq(g)] : ! i [Itm(st, g, i)] : ! c [Cnt(c)] : ! c2 [Inc(c, c2)] : ~C(s, st, c) | ~Eq(g, s, i) | C(s, st2, c2).
    ! s [Shift(s)] : ! st [St(st)] : ! st2 [Nxt(st, st2)] : ! g [Seq(g)] : ! i [Itm(st, g, i)] : ! c [Cnt(c)] : ~C(s, st, c) | Eq(g, s, i) | C(s, st2, c).
    ! s [Shift(s)] : ! st [Lst(st)] : ! c [Cnt(c) & ~Tgt(c)] : ~C(s, st, c).

    ! g [Seq(g)] : D(g, 0, 0).
    ! g [Seq(g)] : ! st [Pos(st)] : ! st2 [Nxt(st, st2)] : ! c [Cnt(c)] : ! c2 [Inc(c, c2)] : ~D(g, st, c) | ~Bit(g, st) | D(g, st2, c2).
    ! g [Seq(g)] : ! st [Pos(st)] : ! st2 [Nxt(st, st2)] : ! c [Cnt(c)] : ~D(g, st, c) | Bit(g, st) | D(g, st2, c).
    ! g [Seq(g)] : ! st [Mid(st)] : ! c [Cnt(c) & ~Hlf(c)] : ~D(g, st, c).
}
"""


def structure(instance):
    l = instance["l"]
    m = (l - 1) // 2
    return {
        "Pos": range(l),
        "Seq": range(2),
        "Sgn": ["neg1", 1],
        "Shift": range(1, m + 1),
        "Pr": [(s, i, (i + s) % l) for s in range(1, m + 1) for i in range(l)],
        "St": range(2 * l + 1),
        "Nxt": [(t, t + 1) for t in range(2 * l)],
        "Itm": [(t, t // l, t % l) for t in range(2 * l)],
        "Cnt": range(2 * l + 1),
        "Inc": [(c, c + 1) for c in range(2 * l)],
        "Tgt": [l - 1],
        "Hlf": [(l + 1) // 2],
        "Mid": [l],
        "Lst": [2 * l],
    }

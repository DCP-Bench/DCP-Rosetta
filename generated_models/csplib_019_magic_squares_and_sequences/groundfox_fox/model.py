# csplib_019_magic_squares_and_sequences: a FOX model for GroundFOX from DCP Rosetta.
#
# A magic sequence of length \( n \) is a sequence of integers \( x_0, \ldots, x_{n-1} \)
# between 0 and \( n-1 \), such that for all \( i \) in 0 to \( n-1 \), the number \( i \)
# occurs exactly \( x_i \) times in the sequence. For instance, 6, 2, 1, 0, 0, 0, 1, 0, 0, 0
# is a magic sequence since 0 occurs 6 times in it, 1 occurs twice, etc.
#
# Print the magic sequence (x).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_019_magic_squares_and_sequences.json --check

# csplib_019_magic_squares_and_sequences: a GroundFOX model of a magic sequence of length n.
# x(p, k): position p holds value k (0..n-1). Count states C(i, j, c): among the first j
# positions exactly c hold the value i. The sequence is magic when, for every position p,
# the final count of value p equals x_p.

FOX = """
invocabulary { Pos/1 Val/1 St/1 Cnt/1 Nxt/2 Inc/2 Last/1 }
outvocabulary { x/2 C/3 }
theory {
    ! p [Pos(p)] : ? k [Val(k)] : x(p, k).
    ! p [Pos(p)] : ! k [Val(k)] : ! m [Val(m) & k ~= m] : ~x(p, k) | ~x(p, m).

    ! i [Val(i)] : C(i, 0, 0).
    ! i [Val(i)] : ! j [St(j)] : ? c [Cnt(c)] : C(i, j, c).
    ! i [Val(i)] : ! j [St(j)] : ! c [Cnt(c)] : ! d [Cnt(d) & c ~= d] : ~C(i, j, c) | ~C(i, j, d).
    ! j [Pos(j)] : ! j2 [Nxt(j, j2)] : ! i [Val(i)] : ! c [Cnt(c)] : ! c2 [Inc(c, c2)] : ~C(i, j, c) | ~x(j, i) | C(i, j2, c2).
    ! j [Pos(j)] : ! j2 [Nxt(j, j2)] : ! i [Val(i)] : ! c [Cnt(c)] : ~C(i, j, c) | x(j, i) | C(i, j2, c).
    ! p [Pos(p)] : ! k [Val(k)] : ! l [Last(l)] : ~x(p, k) | C(p, l, k).
}
"""


def structure(instance):
    n = instance["n"]
    return {
        "Pos": range(n),
        "Val": range(n),
        "St": range(n + 1),
        "Cnt": range(n + 1),
        "Nxt": [(j, j + 1) for j in range(n)],
        "Inc": [(c, c + 1) for c in range(n)],
        "Last": [n],
    }

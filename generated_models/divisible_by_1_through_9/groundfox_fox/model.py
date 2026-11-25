# divisible_by_1_through_9: a FOX model for GroundFOX from DCP Rosetta.
#
# Find a 10 digit number that uses each of the digits 0 to 9 exactly once and where the number
# formed by the first n digits of the number is divisible by n.
#
# You should read the digits of the number from left to right. For example, in the number
# abcd, you need the number a to be divisible by 1, the number ab to be divisible by 2, the
# number abc to be divisible by 3, and the entire number abcd to be divisible by 4.
#
# Print the digits of the number from left to right (digits) as a list of 10 integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py divisible_by_1_through_9.json --check

# divisible_by_1_through_9: a FOX model for GroundFOX from DCP Rosetta.
#
# Find a 10-digit number that uses each of the digits 0..9 exactly once, where the prefix
# of length n is divisible by n for n = 1..10. digits(i, v): the digit at position i
# (0-based, read left to right) is v.
#
# Divisibility as a modular chain: the prefix of length n has value sum_{i<n} d_i * 10^(n-1-i),
# so it is divisible by n iff sum_{i<n} d_i * c(n, i) = 0 (mod n) with c(n, i) = 10^(n-1-i) mod n.
# acc(n, i, s) says the partial sum of the first i digits, for modulus n, is s (mod n).
# The arithmetic table Tr(n, i, s, v, t) with t = (s + c(n, i) * v) mod n is computed in
# structure(); the sentences say the chain moves forward with the digits, and that the
# final residue is 0. No ground clauses are generated in Python.
LENGTH = 10


def _table():
    rows = []
    for n in range(1, LENGTH + 1):
        for i in range(n):
            c = pow(10, n - 1 - i, n)
            for s in range(n):
                for v in range(10):
                    rows.append((n, i, s, v, (s + c * v) % n))
    return rows


FOX = """
invocabulary { Mod/1 Pos/1 Nxt/2 Res/1 Dig/1 Tr/5 }
outvocabulary { digits/2 acc/3 }
theory {
    ! i [Pos(i)] : ? v [Dig(v)] : digits(i, v).
    ! i [Pos(i)] : ! v [Dig(v)] : ! w [Dig(w) & ~(v = w)] : ~digits(i, v) | ~digits(i, w).
    ! v [Dig(v)] : ? i [Pos(i)] : digits(i, v).
    ! v [Dig(v)] : ! i [Pos(i)] : ! j [Pos(j) & ~(i = j)] : ~digits(i, v) | ~digits(j, v).

    ! n [Mod(n)] : acc(n, 0, 0).
    ! n [Mod(n)] : ! i [Pos(i)] : ! j [Nxt(i, j)] : ! s [Res(s)] : ! v [Dig(v)] : ! t [Tr(n, i, s, v, t)] : ~acc(n, i, s) | ~digits(i, v) | acc(n, j, t).
    ! n [Mod(n)] : ! s [Res(s) & ~(s = 0)] : ~acc(n, n, s).
}
"""


def structure(instance):
    return {
        "domain": list(range(LENGTH + 1)),
        "Mod": list(range(1, LENGTH + 1)),
        "Pos": list(range(LENGTH)),
        "Nxt": [(i, i + 1) for i in range(LENGTH)],
        "Res": list(range(LENGTH)),
        "Dig": list(range(10)),
        "Tr": _table(),
    }

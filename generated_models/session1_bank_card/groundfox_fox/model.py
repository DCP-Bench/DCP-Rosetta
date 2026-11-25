# session1_bank_card: a FOX model for GroundFOX from DCP Rosetta.
#
# My bank card has a 4 digit pin, abcd. I use the following facts to help me remember it:
#
# - no two digits are the same - the 2-digit number cd is 3 times the 2-digit number ab - the
# 2-digit number da is 2 times the 2-digit number bc
#
# Print the PIN (a, b, c, d).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session1_bank_card.json --check

# session1_bank_card: a FOX model for GroundFOX from DCP Rosetta.
#
# PIN abcd: the two-digit numbers ab, cd, bc, da satisfy cd = 3*ab and da = 2*bc, and
# all four digits are different. Each digit is one-hot over 0..9 (a(v) means a = v).
# The two equations are allowed-tuple relations of one constraint each (Ok1, Ok2); the
# sentences forbid every digit tuple outside them. Distinctness is a pairwise sentence.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

import itertools

FOX = """
invocabulary { Val/1 Ok1/4 Ok2/4 }
outvocabulary { a/1 b/1 c/1 d/1 }
theory {
    ? v [Val(v)] : a(v).
    ? v [Val(v)] : b(v).
    ? v [Val(v)] : c(v).
    ? v [Val(v)] : d(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~a(v) | ~a(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~b(v) | ~b(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~c(v) | ~c(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~d(v) | ~d(w).
    ! v [Val(v)] : ~a(v) | ~b(v).
    ! v [Val(v)] : ~a(v) | ~c(v).
    ! v [Val(v)] : ~a(v) | ~d(v).
    ! v [Val(v)] : ~b(v) | ~c(v).
    ! v [Val(v)] : ~b(v) | ~d(v).
    ! v [Val(v)] : ~c(v) | ~d(v).
    ! p [Val(p)] : ! q [Val(q)] : ! r [Val(r)] : ! s [Val(s) & ~Ok1(p, q, r, s)] : ~a(p) | ~b(q) | ~c(r) | ~d(s).
    ! p [Val(p)] : ! q [Val(q)] : ! r [Val(r)] : ! s [Val(s) & ~Ok2(p, q, r, s)] : ~a(p) | ~b(q) | ~c(r) | ~d(s).
}
"""


def structure(instance):
    digits = range(10)
    # Ok1: cd = 3*ab, as (a, b, c, d).  Ok2: da = 2*bc, as (a, b, c, d).
    ok1 = [(a, b, c, d) for a, b, c, d in itertools.product(digits, repeat=4)
           if 10 * c + d == 3 * (10 * a + b)]
    ok2 = [(a, b, c, d) for a, b, c, d in itertools.product(digits, repeat=4)
           if 10 * d + a == 2 * (10 * b + c)]
    return {"Val": digits, "Ok1": ok1, "Ok2": ok2}

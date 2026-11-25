# hanging_weights: a FOX model for GroundFOX from DCP Rosetta.
#
# The diagram below is a bunch of weights (A-M) hanging from a system of bars. The weights
# have different integer values between 1 and 13, and the goal is to figure out what each
# weight must be for the diagram below to balance correctly as shown. Each three characters
# along a bar are one unit of distance:
#
# ```text | | +--+--+--+--+--+--+--+ | | | | +--+--+--+--+--+ | | L M | | |
# +--+--+--+--+--+--+ +--+--+--+--+--+ H | I | J K | | | | +--+--+--+--+--+ | +--+--+--+--+--+
# E F | G | | | +--+--+--+--+--+ +--+--+--+--+--+--+ A B C D ```
#
# The rules for this kind of puzzle are: (1) The weights on either side of a given pivot point
# must be equal, when weighted by the distance from the pivot, and (2) a bar hanging beneath
# another contributes its total weight as though it were a single weight. For instance, the
# bar on the bottom right must have `5*C=D`, and the one above it must have `3*G=2*(C+D)`.
#
# Print the weights (a, b, c, d, e, f, g, h, i, j, k, l, m) that satisfy the conditions above.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py hanging_weights.json --check

# hanging_weights: a GroundFOX model. Weights a..m (a=0 ... m=12 in the brief's order) each take a
# value in 1..13, pairwise different. The balance equations are first-order sentences over
# arithmetic data relations; sums of weights are auxiliary outputs defined by sentences.
# structure() only supplies the arithmetic tables (addition, scaling, equality), never values.

FOX = """
invocabulary { Val/1 Num/1 Sr/1 Add/3 Lin32/3 Lin21/3 Lin4/3 T4/2 T5/2 T32/2 T43/2 Id/2 Ok6/3 }
outvocabulary { a/1 b/1 c/1 d/1 e/1 f/1 g/1 h/1 i/1 j/1 k/1 l/1 m/1
                P/1 Q/1 R/1 H/1 A/1 JK/1 G/1 JKG/1 JKGP/1 W1/1 W2/1 S4/1 Lhs/1 Rhs/1 Tl/1 }
theory {
    ? v [Val(v)] : a(v).
    ? v [Val(v)] : b(v).
    ? v [Val(v)] : c(v).
    ? v [Val(v)] : d(v).
    ? v [Val(v)] : e(v).
    ? v [Val(v)] : f(v).
    ? v [Val(v)] : g(v).
    ? v [Val(v)] : h(v).
    ? v [Val(v)] : i(v).
    ? v [Val(v)] : j(v).
    ? v [Val(v)] : k(v).
    ? v [Val(v)] : l(v).
    ? v [Val(v)] : m(v).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~a(v) | ~a(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~b(v) | ~b(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~c(v) | ~c(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~d(v) | ~d(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~e(v) | ~e(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~f(v) | ~f(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~g(v) | ~g(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~h(v) | ~h(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~i(v) | ~i(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~j(v) | ~j(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~k(v) | ~k(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~l(v) | ~l(w).
    ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~m(v) | ~m(w).
    ! v [Val(v)] : ~a(v) | ~b(v).
    ! v [Val(v)] : ~a(v) | ~c(v).
    ! v [Val(v)] : ~a(v) | ~d(v).
    ! v [Val(v)] : ~a(v) | ~e(v).
    ! v [Val(v)] : ~a(v) | ~f(v).
    ! v [Val(v)] : ~a(v) | ~g(v).
    ! v [Val(v)] : ~a(v) | ~h(v).
    ! v [Val(v)] : ~a(v) | ~i(v).
    ! v [Val(v)] : ~a(v) | ~j(v).
    ! v [Val(v)] : ~a(v) | ~k(v).
    ! v [Val(v)] : ~a(v) | ~l(v).
    ! v [Val(v)] : ~a(v) | ~m(v).
    ! v [Val(v)] : ~b(v) | ~c(v).
    ! v [Val(v)] : ~b(v) | ~d(v).
    ! v [Val(v)] : ~b(v) | ~e(v).
    ! v [Val(v)] : ~b(v) | ~f(v).
    ! v [Val(v)] : ~b(v) | ~g(v).
    ! v [Val(v)] : ~b(v) | ~h(v).
    ! v [Val(v)] : ~b(v) | ~i(v).
    ! v [Val(v)] : ~b(v) | ~j(v).
    ! v [Val(v)] : ~b(v) | ~k(v).
    ! v [Val(v)] : ~b(v) | ~l(v).
    ! v [Val(v)] : ~b(v) | ~m(v).
    ! v [Val(v)] : ~c(v) | ~d(v).
    ! v [Val(v)] : ~c(v) | ~e(v).
    ! v [Val(v)] : ~c(v) | ~f(v).
    ! v [Val(v)] : ~c(v) | ~g(v).
    ! v [Val(v)] : ~c(v) | ~h(v).
    ! v [Val(v)] : ~c(v) | ~i(v).
    ! v [Val(v)] : ~c(v) | ~j(v).
    ! v [Val(v)] : ~c(v) | ~k(v).
    ! v [Val(v)] : ~c(v) | ~l(v).
    ! v [Val(v)] : ~c(v) | ~m(v).
    ! v [Val(v)] : ~d(v) | ~e(v).
    ! v [Val(v)] : ~d(v) | ~f(v).
    ! v [Val(v)] : ~d(v) | ~g(v).
    ! v [Val(v)] : ~d(v) | ~h(v).
    ! v [Val(v)] : ~d(v) | ~i(v).
    ! v [Val(v)] : ~d(v) | ~j(v).
    ! v [Val(v)] : ~d(v) | ~k(v).
    ! v [Val(v)] : ~d(v) | ~l(v).
    ! v [Val(v)] : ~d(v) | ~m(v).
    ! v [Val(v)] : ~e(v) | ~f(v).
    ! v [Val(v)] : ~e(v) | ~g(v).
    ! v [Val(v)] : ~e(v) | ~h(v).
    ! v [Val(v)] : ~e(v) | ~i(v).
    ! v [Val(v)] : ~e(v) | ~j(v).
    ! v [Val(v)] : ~e(v) | ~k(v).
    ! v [Val(v)] : ~e(v) | ~l(v).
    ! v [Val(v)] : ~e(v) | ~m(v).
    ! v [Val(v)] : ~f(v) | ~g(v).
    ! v [Val(v)] : ~f(v) | ~h(v).
    ! v [Val(v)] : ~f(v) | ~i(v).
    ! v [Val(v)] : ~f(v) | ~j(v).
    ! v [Val(v)] : ~f(v) | ~k(v).
    ! v [Val(v)] : ~f(v) | ~l(v).
    ! v [Val(v)] : ~f(v) | ~m(v).
    ! v [Val(v)] : ~g(v) | ~h(v).
    ! v [Val(v)] : ~g(v) | ~i(v).
    ! v [Val(v)] : ~g(v) | ~j(v).
    ! v [Val(v)] : ~g(v) | ~k(v).
    ! v [Val(v)] : ~g(v) | ~l(v).
    ! v [Val(v)] : ~g(v) | ~m(v).
    ! v [Val(v)] : ~h(v) | ~i(v).
    ! v [Val(v)] : ~h(v) | ~j(v).
    ! v [Val(v)] : ~h(v) | ~k(v).
    ! v [Val(v)] : ~h(v) | ~l(v).
    ! v [Val(v)] : ~h(v) | ~m(v).
    ! v [Val(v)] : ~i(v) | ~j(v).
    ! v [Val(v)] : ~i(v) | ~k(v).
    ! v [Val(v)] : ~i(v) | ~l(v).
    ! v [Val(v)] : ~i(v) | ~m(v).
    ! v [Val(v)] : ~j(v) | ~k(v).
    ! v [Val(v)] : ~j(v) | ~l(v).
    ! v [Val(v)] : ~j(v) | ~m(v).
    ! v [Val(v)] : ~k(v) | ~l(v).
    ! v [Val(v)] : ~k(v) | ~m(v).
    ! v [Val(v)] : ~l(v) | ~m(v).

    ! x [Val(x)] : ! y [Val(y) & ~T4(x, y)] : ~a(x) | ~b(y).
    ! x [Val(x)] : ! y [Val(y) & ~T5(x, y)] : ~c(x) | ~d(y).
    ! x [Val(x)] : ! y [Val(y) & ~T32(x, y)] : ~e(x) | ~f(y).

    ! x [Val(x)] : ! y [Val(y)] : ! s [Add(x, y, s)] : ~a(x) | ~b(y) | P(s).
    ! x [Val(x)] : ! y [Val(y)] : ! s [Add(x, y, s)] : ~c(x) | ~d(y) | Q(s).
    ! x [Val(x)] : ! y [Val(y)] : ! s [Add(x, y, s)] : ~e(x) | ~f(y) | R(s).
    ! x [Val(x)] : ! y [Val(y)] : ! s [Add(x, y, s)] : ~h(x) | ~i(y) | H(s).
    ! x [Val(x)] : ! y [Val(y)] : ! s [Add(x, y, s)] : ~l(x) | ~m(y) | A(s).
    ! x [Val(x)] : ! y [Val(y)] : ! s [Add(x, y, s)] : ~j(x) | ~k(y) | JK(s).

    ! x [Val(x)] : ! y [Num(y)] : ! s [Add(x, y, s)] : ~g(x) | ~Q(y) | G(s).
    ! x [Val(x)] : ! q [Num(q) & ~T32(x, q)] : ~g(x) | ~Q(q).

    ! x [Val(x)] : ! r [Sr(r)] : ! y [Val(y) & ~Ok6(x, r, y)] : ~h(x) | ~R(r) | ~i(y).

    ! x [Num(x)] : ! y [Val(y)] : ! s [Lin32(x, y, s)] : ~P(x) | ~j(y) | Lhs(s).
    ! x [Num(x)] : ! y [Val(y)] : ! s [Lin21(x, y, s)] : ~G(x) | ~k(y) | Rhs(s).
    ! l [Num(l)] : ! r [Num(r) & ~Id(l, r)] : ~Lhs(l) | ~Rhs(r).

    ! x [Num(x)] : ! y [Num(y)] : ! s [Add(x, y, s)] : ~H(x) | ~R(y) | S4(s).
    ! x [Val(x)] : ! y [Val(y)] : ! s [Lin4(x, y, s)] : ~m(x) | ~l(y) | Tl(s).
    ! x [Num(x)] : ! y [Num(y) & ~Id(x, y)] : ~S4(x) | ~Tl(y).

    ! x [Num(x)] : ! y [Num(y)] : ! s [Add(x, y, s)] : ~A(x) | ~S4(y) | W1(s).
    ! x [Num(x)] : ! y [Val(y)] : ! s [Add(x, y, s)] : ~JK(x) | ~g(y) | JKG(s).
    ! x [Num(x)] : ! y [Num(y)] : ! s [Add(x, y, s)] : ~JKG(x) | ~P(y) | JKGP(s).
    ! x [Num(x)] : ! y [Num(y)] : ! s [Add(x, y, s)] : ~JKGP(x) | ~Q(y) | W2(s).
    ! x [Num(x)] : ! y [Num(y) & ~T43(x, y)] : ~W1(x) | ~W2(y).
}
"""


def structure(instance):
    top = 104
    num = list(range(0, top + 1))
    val = list(range(1, 14))
    return {
        "Val": val,
        "Num": num,
        "Sr": list(range(2, 27)),
        # sums: x + y = s over the numeric domain
        "Add": [(x, y, s) for x in num for y in num for s in [x + y] if s <= top],
        # 3x + 2y = s  (x a sum, y a weight)
        "Lin32": [(x, y, 3 * x + 2 * y) for x in num for y in val if 3 * x + 2 * y <= top],
        # 2x + y = s  (x a sum, y a weight)
        "Lin21": [(x, y, 2 * x + y) for x in num for y in val if 2 * x + y <= top],
        # s = l + 4m  (x = m, y = l)
        "Lin4": [(x, y, y + 4 * x) for x in val for y in val if y + 4 * x <= top],
        # scalar relations between two values
        "T4": [(x, 4 * x) for x in val if 4 * x in val],
        "T5": [(x, 5 * x) for x in val if 5 * x in val],
        "T32": [(x, y) for x in num for y in num if 3 * x == 2 * y],
        "T43": [(x, y) for x in num for y in num if 4 * x == 3 * y],
        "Id": [(x, x) for x in num],
        # 3x = 2r + 3y : allowed (h, R, i) triples of the bar balance
        "Ok6": [(x, r, y) for x in val for r in range(2, 27) for y in val if 3 * x == 2 * r + 3 * y],
    }

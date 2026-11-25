# frog_circle: a FOX model for GroundFOX from DCP Rosetta.
#
# Cards numbered 1 to n are arranged in a circle. A frog jumps on card 1, then jumps to the
# card 1 place clockwise around the circle. Then, from card k, he jumps directly to the card k
# places clockwise around the circle. The frog continues jumping in this way forever.
#
# Find an arrangement of cards that allows the frog to jump on every card starting from card
# 1.
#
# Print the card arrangement (x) that satisfies the above condition, as a list of n different
# integers each from 1 to n.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py frog_circle.json --check

# frog_circle: a FOX model for GroundFOX from DCP Rosetta.
#
# Arrange cards 1..n on a circle (x[p] is the card at position p) so that the frog,
# starting on card 1 and jumping k places clockwise from card k, visits every card.
# The frog's walk is P(k, q): after k jumps it is on position q. Coverage of all
# positions by the n steps of the walk means the jump map is a single n-cycle.

FOX = """
invocabulary { Pos/1 Val/1 Step/1 Succ/2 Jump/3 Zero/1 }
outvocabulary { x/2 path/2 }
theory {
    ! q [Zero(q)] : x(q, 1).
    ! q [Pos(q)] : ? v [Val(v)] : x(q, v).
    ! q [Pos(q)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~x(q, v) | ~x(q, w).
    ! v [Val(v)] : ! q [Pos(q)] : ! r [Pos(r) & q ~= r] : ~x(q, v) | ~x(r, v).
    ! q [Pos(q)] : ~x(q, 1) | path(0, q).
    ! q [Pos(q)] : ~path(0, q) | x(q, 1).
    ! k [Step(k)] : ! q [Pos(q)] : ! r [Pos(r) & q ~= r] : ~path(k, q) | ~path(k, r).
    ! q [Pos(q)] : ? k [Step(k)] : path(k, q).
    ! k [Step(k)] : ! k2 [Succ(k, k2)] : ! q [Pos(q)] : ! v [Val(v)] : ! r [Jump(q, v, r)] : ~path(k, q) | ~x(q, v) | path(k2, r).
}
"""


def structure(instance):
    n = instance["n"]
    return {
        "Pos": list(range(n)),
        "Val": list(range(1, n + 1)),
        "Step": list(range(n)),
        "Zero": [0],
        "Succ": [(k, k + 1) for k in range(n - 1)],
        "Jump": [(p, v, (p + v) % n) for p in range(n) for v in range(1, n + 1)],
    }

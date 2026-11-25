# giant_cat_army: a FOX model for GroundFOX from DCP Rosetta.
#
# Basically you start with [0], then you build this list by using one of three operations:
# adding 5, adding 7, or taking sqrt. You successfully complete the game when you have managed
# to build a list such that 2,10 and 14 appear on the list, in that order, and there can be
# other numbers between them.
#
# The rules also require that all the elements are distinct, they're all <=60 and are all only
# integers. For example, starting with [0], you can apply (add5, add7, add5), which would
# result in [0, 5, 12, 17], but since it doesn't have 2,10,14 in that order it doesn't satisfy
# the game.
#
# Print the sequence of integers (x) that satisfies the above conditions in the correct order
# starting from 0, ending with 14, and has length of 24.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py giant_cat_army.json --check

# giant_cat_army: a FOX model for GroundFOX from DCP Rosetta.

FOX = """
invocabulary { Pos/1 Nxt/2 First/1 Last/1 Val/1 Lt/2 Step/2 }
outvocabulary { x/2 s2/1 got/1 }
theory {
    ! p [First(p)] : x(p, 0).
    ! p [Last(p)] : x(p, 14).
    ! p [Pos(p)] : ? v [Val(v)] : x(p, v).
    ! p [Pos(p)] : ! v [Val(v)] : ! w [Val(w) & Lt(v, w)] : ~x(p, v) | ~x(p, w).
    ! p [Pos(p)] : ! q [Pos(q) & Lt(p, q)] : ! v [Val(v)] : ~x(p, v) | ~x(q, v).
    ! p [Pos(p)] : ! q [Nxt(p, q)] : ! a [Val(a) & ~? b : Step(a, b)] : ~x(p, a).
    ! p [Pos(p)] : ! q [Nxt(p, q)] : ! a [Val(a) & ? b : Step(a, b)] : ? b [Step(a, b)] : x(q, b) | ~x(p, a).
    ! p [Pos(p)] : ~x(p, 2) | s2(p).
    ! q [Pos(q)] : ! p [Nxt(p, q)] : ~s2(q) | s2(p) | x(q, 2).
    ! p [First(p)] : ~s2(p) | x(p, 2).
    ! p [First(p)] : ~got(p).
    ! q [Pos(q)] : ! p [Nxt(p, q)] : ~got(q) | got(p) | x(q, 10).
    ! q [Pos(q)] : ! p [Nxt(p, q)] : ~got(q) | got(p) | s2(p).
    ! p [Last(p)] : got(p).
}
"""


def structure(instance):
    # Operations: add 5, add 7, integer square root (a = b*b maps to b); values in 0..60.
    top = 60
    step = set()
    for a in range(top + 1):
        for d in (5, 7):
            if a + d <= top:
                step.add((a, a + d))
    for b in range(top + 1):
        if b * b <= top:
            step.add((b * b, b))
    return {
        "Pos": range(24),
        "Nxt": [(p, p + 1) for p in range(23)],
        "First": [0],
        "Last": [23],
        "Val": range(top + 1),
        "Lt": [(a, b) for a in range(top + 1) for b in range(a + 1, top + 1)],
        "Step": sorted(step),
    }

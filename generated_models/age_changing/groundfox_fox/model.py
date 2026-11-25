# age_changing: a FOX model for GroundFOX from DCP Rosetta.
#
# If you start with my age, in years, and apply the four operations +2, /8, -3 and *7 in some
# order, then the final answer you get is my husband's age.
#
# Funnily enough, if you start with his age and apply the same four operations in a different
# order, then you get my age.
#
# Both ages are between 16 and 120, and every intermediate result is a positive integer, so a
# division by 8 must be exact.
#
# What are our two ages?
#
# Print my age and my husband's age (m, h).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py age_changing.json --check

# age_changing: a FOX model for GroundFOX from DCP Rosetta.
#
# Joe's (my) age m and husband's age h, both in 16..120. Applying +2, /8 (exact), -3 and *7
# in some order to m gives h; applying the same four operations in a different order to h
# gives m. Intermediate results are positive integers.
#
# Two chains of four steps. Step k of chain c applies one operation o_c(k, t) (t: 0 = +2,
# 1 = -3, 2 = *7, 3 = /8); each operation is a data relation Rel(t, v, w) over the values
# 1..B, with Def(t, v) where the operation is defined. The theory is fixed text: the
# layered states st_c(k, v) hold the intermediate value after k steps.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

B = 1000  # bound on intermediate values (the largest reachable value from ages <= 120 is 854)

FOX = """
invocabulary { Val/1 Age/1 Lay/1 Stp/1 Nxt/2 Op/1 Rel/3 Def/2 Pair/1 PK/2 PT/2 }
outvocabulary { m/1 h/1 o1/2 o2/2 dp/1 st1/2 st2/2 }
theory {
    ? v [Age(v)] : m(v).
    ! v [Age(v)] : ! w [Age(w) & v ~= w] : ~m(v) | ~m(w).
    ! v [~Age(v)] : ~m(v).
    ? v [Age(v)] : h(v).
    ! v [Age(v)] : ! w [Age(w) & v ~= w] : ~h(v) | ~h(w).
    ! v [~Age(v)] : ~h(v).

    ! v [Val(v)] : ~m(v) | st1(0, v).
    ! v [Val(v)] : ~st1(0, v) | m(v).
    ! v [Val(v)] : ~h(v) | st1(4, v).
    ! v [Val(v)] : ~st1(4, v) | h(v).
    ! v [Val(v)] : ~h(v) | st2(0, v).
    ! v [Val(v)] : ~st2(0, v) | h(v).
    ! v [Val(v)] : ~m(v) | st2(4, v).
    ! v [Val(v)] : ~st2(4, v) | m(v).

    ! k [Stp(k)] : ? t [Op(t)] : o1(k, t).
    ! k [Stp(k)] : ! t [Op(t)] : ! u [Op(u) & t ~= u] : ~o1(k, t) | ~o1(k, u).
    ! t [Op(t)] : ? k [Stp(k)] : o1(k, t).
    ! t [Op(t)] : ! k [Stp(k)] : ! l [Stp(l) & k ~= l] : ~o1(k, t) | ~o1(l, t).

    ! k [Stp(k)] : ? t [Op(t)] : o2(k, t).
    ! k [Stp(k)] : ! t [Op(t)] : ! u [Op(u) & t ~= u] : ~o2(k, t) | ~o2(k, u).
    ! t [Op(t)] : ? k [Stp(k)] : o2(k, t).
    ! t [Op(t)] : ! k [Stp(k)] : ! l [Stp(l) & k ~= l] : ~o2(k, t) | ~o2(l, t).

    ! p [Pair(p)] : ! k [PK(p, k)] : ! t [PT(p, t)] : ~dp(p) | o1(k, t).
    ! p [Pair(p)] : ! k [PK(p, k)] : ! t [PT(p, t)] : ~dp(p) | ~o2(k, t).
    ? p [Pair(p)] : dp(p).

    ! j [Lay(j)] : ! k [Nxt(j, k)] : ! t [Op(t)] : ! v [Val(v) & ~Def(t, v)] : ~o1(k, t) | ~st1(j, v).
    ! j [Lay(j)] : ! k [Nxt(j, k)] : ! t [Op(t)] : ! v [Val(v)] : ! w [Rel(t, v, w)] : ~o1(k, t) | ~st1(j, v) | st1(k, w).
    ! j [Lay(j)] : ! k [Nxt(j, k)] : ! t [Op(t)] : ! v [Val(v) & ~Def(t, v)] : ~o2(k, t) | ~st2(j, v).
    ! j [Lay(j)] : ! k [Nxt(j, k)] : ! t [Op(t)] : ! v [Val(v)] : ! w [Rel(t, v, w)] : ~o2(k, t) | ~st2(j, v) | st2(k, w).
}
"""


def structure(instance):
    vals = range(1, B + 1)
    rel = []
    for v in vals:
        if v + 2 <= B:
            rel.append((0, v, v + 2))
        if v - 3 >= 1:
            rel.append((1, v, v - 3))
        if 7 * v <= B:
            rel.append((2, v, 7 * v))
        if v % 8 == 0 and v // 8 >= 1:
            rel.append((3, v, v // 8))
    defined = sorted({(t, v) for t, v, _w in rel})
    return {
        "domain": range(0, B + 1),
        "Val": vals,
        "Age": range(16, 121),
        "Lay": range(0, 4),
        "Stp": range(1, 5),
        "Nxt": [(0, 1), (1, 2), (2, 3), (3, 4)],
        "Op": range(0, 4),
        "Rel": rel,
        "Def": defined,
        "Pair": range(0, 16),
        "PK": [(4 * (k - 1) + t, k) for k in range(1, 5) for t in range(4)],
        "PT": [(4 * (k - 1) + t, t) for k in range(1, 5) for t in range(4)],
    }

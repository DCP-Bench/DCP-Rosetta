# csplib_049_number_partitioning: a FOX model for GroundFOX from DCP Rosetta.
#
# This problem consists of finding a partition of numbers 1..N into two sets A and B such
# that:
#
# - A and B have the same cardinality - Sum of numbers in A = sum of numbers in B - Sum of
# squares of numbers in A = sum of squares of numbers in B
#
# There is no solution for \( N < 8 \).
#
# Here is an example for \( N = 8 \): A = (1, 4, 6, 7) and B = (2, 3, 5, 8)
#
# Print the sets A and B (A, B).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_049_number_partitioning.json --check

# csplib_049_number_partitioning: a FOX model for GroundFOX from DCP Rosetta.
#
# Partition the numbers 1..N into two sets A and B of equal cardinality, with equal sums and
# equal sums of squares. Print the sets (A, B).
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

# InA(v) says v is in A. Two layered chains of partial sums (of v and of v*v over A) are walked
# backwards from the target: a state at layer v with v in A has a predecessor at layer v-1
# shifted by v (or v*v), otherwise the same state. Both chains start at 0 in layer 0.
FOX = """
invocabulary { Num/1 Pos/1 Pu/2 BsS/3 BsQ/3 SSt/1 SBad/1 QSt/1 QBad/1 Zero/1 Last/1 STarget/1 QTarget/1 }
outvocabulary { A/2 B/2 InA/1 Cs/2 Cq/2 }
theory {
    ! p [Pos(p)] : ? v [Num(v)] : A(p,v).
    ! p [Pos(p)] : ! v [Num(v)] : ! w [Num(w) & v ~= w] : ~A(p,v) | ~A(p,w).
    ! p [Pos(p)] : ? v [Num(v)] : B(p,v).
    ! p [Pos(p)] : ! v [Num(v)] : ! w [Num(w) & v ~= w] : ~B(p,v) | ~B(p,w).
    ! p [Pos(p)] : ! q [Pos(q) & p ~= q] : ! v [Num(v)] : ~A(p,v) | ~A(q,v).
    ! p [Pos(p)] : ! q [Pos(q) & p ~= q] : ! v [Num(v)] : ~B(p,v) | ~B(q,v).
    ! p [Pos(p)] : ! v [Num(v)] : ~A(p,v) | InA(v).
    ! p [Pos(p)] : ! v [Num(v)] : ~B(p,v) | ~InA(v).

    ! y [Zero(y)] : Cs(0,y).
    ! y [SSt(y) & ~Zero(y)] : ~Cs(0,y).
    ! y [SBad(y)] : ~Cs(0,y).
    ! v [Num(v)] : ! y [SBad(y)] : ~Cs(v,y).
    ! v [Num(v)] : ! u [Pu(v,u)] : ! y [SSt(y)] : ! x [BsS(v,y,x)] : ~Cs(v,y) | ~InA(v) | Cs(u,x).
    ! v [Num(v)] : ! u [Pu(v,u)] : ! y [SSt(y)] : ~Cs(v,y) | InA(v) | Cs(u,y).
    ! v [Last(v)] : ! y [SSt(y) & ~STarget(y)] : ~Cs(v,y).
    ! v [Last(v)] : ? y [STarget(y)] : Cs(v,y).

    ! y [Zero(y)] : Cq(0,y).
    ! y [QSt(y) & ~Zero(y)] : ~Cq(0,y).
    ! y [QBad(y)] : ~Cq(0,y).
    ! v [Num(v)] : ! y [QBad(y)] : ~Cq(v,y).
    ! v [Num(v)] : ! u [Pu(v,u)] : ! y [QSt(y)] : ! x [BsQ(v,y,x)] : ~Cq(v,y) | ~InA(v) | Cq(u,x).
    ! v [Num(v)] : ! u [Pu(v,u)] : ! y [QSt(y)] : ~Cq(v,y) | InA(v) | Cq(u,y).
    ! v [Last(v)] : ! y [QSt(y) & ~QTarget(y)] : ~Cq(v,y).
    ! v [Last(v)] : ? y [QTarget(y)] : Cq(v,y).
}
"""


def structure(instance):
    n = instance["n"]
    m = n // 2
    s_total = n * (n + 1) // 2           # sum of 1..n
    q_total = n * (n + 1) * (2 * n + 1) // 6  # sum of squares of 1..n
    s_bad, q_bad = s_total + 1, q_total + 1
    # Equal cardinality and equal sums need an even n and an even total; otherwise no target.
    s_target = [s_total // 2] if n % 2 == 0 and s_total % 2 == 0 else []
    q_target = [q_total // 2] if n % 2 == 0 and q_total % 2 == 0 else []
    numbers = list(range(1, n + 1))
    s_states = list(range(s_total + 1))
    q_states = list(range(q_total + 1))
    bs_s, bs_q = [], []
    for v in numbers:
        for y in s_states:
            bs_s.append((v, y, y - v if y >= v else s_bad))
        for y in q_states:
            bs_q.append((v, y, y - v * v if y >= v * v else q_bad))
    return {
        "domain": list(range(0, max(q_bad, n) + 2)),
        "Num": numbers,
        "Pos": list(range(m)),
        "Pu": [(v, v - 1) for v in numbers],
        "BsS": bs_s,
        "BsQ": bs_q,
        "SSt": s_states,
        "SBad": [s_bad],
        "QSt": q_states,
        "QBad": [q_bad],
        "Zero": [0],
        "Last": [n],
        "STarget": s_target,
        "QTarget": q_target,
    }

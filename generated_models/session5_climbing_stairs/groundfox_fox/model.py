# session5_climbing_stairs: a FOX model for GroundFOX from DCP Rosetta.
#
# We want to climb a stair of n steps with a number of steps at a time, within a given range
# [m1, m2]. For example a stair of 4 steps with m1 = 1, and m2 = 2 can be climbed with a
# sequence of four one-step moves or with two two-steps moves. Find a way to climb a stair of
# n steps, i.e. you can take only m1 to m2 steps at a time.
#
# Print the number of steps (steps) taken at each move as a list of n integers, where each
# integer is between m1 and m2, or 0 if no steps are taken at that move, i.e. after we reach
# the top of the stair.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_climbing_stairs.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session5_climbing_stairs.json --check

# session5_climbing_stairs: a FOX model for GroundFOX from DCP Rosetta.
#
# Climb n steps taking m1..m2 steps per move. steps[i] is the move at index i (0 once
# the top is reached). st(i, s) is the running total before move i; the transitions
# are precomputed from the instance (Add: the legal (total, move, new total) triples).

FOX = """
invocabulary { Stage/1 Move/1 Val/1 First/1 Last/1 Nxt/2 Add/3 Ok/2 Target/1 }
outvocabulary { steps/2 st/2 }
theory {
    ! i [Move(i)] : ? v [Val(v)] : steps(i, v).
    ! i [Move(i)] : ! v [Val(v)] : ! w [Val(w) & v ~= w] : ~steps(i, v) | ~steps(i, w).
    ! i [First(i)] : st(i, 0).
    ! i [Move(i)] : ! s [Stage(s)] : ! v [Val(v) & ~Ok(s, v)] : ~st(i, s) | ~steps(i, v).
    ! i [Move(i)] : ! j [Nxt(i, j)] : ! s [Stage(s)] : ! v [Val(v)] : ! t [Stage(t) & Add(s, v, t)] : ~st(i, s) | ~steps(i, v) | st(j, t).
    ! i [Last(i)] : ! s [Stage(s) & ~Target(s)] : ~st(i, s).
}
"""


def structure(instance):
    n = instance["n"]
    m1 = instance["m1"]
    m2 = instance["m2"]
    add = []
    for s in range(n + 1):
        if s == n:
            add.append((s, 0, n))
        else:
            for v in range(max(m1, 1), m2 + 1):
                if s + v <= n:
                    add.append((s, v, s + v))
    ok = sorted({(s, v) for s, v, _ in add})
    return {
        "Stage": list(range(n + 1)),
        "Move": list(range(n)),
        "Val": list(range(n + 1)),
        "First": [0],
        "Last": [n],
        "Nxt": [(i, i + 1) for i in range(n)],
        "Add": add,
        "Ok": ok,
        "Target": [n],
    }

# csplib_010_social_golfers_problem: a FOX model for GroundFOX from DCP Rosetta.
#
# The coordinator of a local golf club has come to you with the following problem. In their
# club, there are `n_groups * group_size` golfers, each of whom play golf once a week, and
# always in `n_groups` groups of `group_size` golfers. They would like you to come up with a
# schedule of play for these golfers over `n_weeks` weeks, such that no golfer plays in the
# same group as any other golfer on more than one occasion.
#
# Print the assignments of golfers to groups for each week (assign) as a list of lists of
# integers - 0-indexed; assign[i][j] is the group number of golfer i in week j.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_010_social_golfers_problem.json --check

# csplib_010_social_golfers_problem: a FOX model for GroundFOX from DCP Rosetta.
#
# n_groups * group_size golfers play n_weeks weeks, each week in n_groups groups of
# group_size golfers, such that no two golfers share a group more than once.
# Output assign[i][j]: the group of golfer i in week j (0-based).

FOX = """
invocabulary { Golf/1 Week/1 Grp/1 Pref/1 Cnt/1 Start/1 Last/1 Full/1 NotFull/1 Next/2 Succ/2 Lt/2 }
outvocabulary { assign/3 St/4 SameG/3 }
theory {
    ! i [Golf(i)] : ! w [Week(w)] : ? k [Grp(k)] : assign(i, w, k).
    ! i [Golf(i)] : ! w [Week(w)] : ! k [Grp(k)] : ! k2 [Grp(k2) & k ~= k2] : ~assign(i, w, k) | ~assign(i, w, k2).
    ! w [Week(w)] : ! k [Grp(k)] : ! i [Start(i)] : ! c [Start(c)] : St(w, k, i, c).
    ! w [Week(w)] : ! k [Grp(k)] : ! i [Pref(i)] : ? c [Cnt(c)] : St(w, k, i, c).
    ! w [Week(w)] : ! k [Grp(k)] : ! i [Pref(i)] : ! c [Cnt(c)] : ! d [Cnt(d) & c ~= d] : ~St(w, k, i, c) | ~St(w, k, i, d).
    ! w [Week(w)] : ! k [Grp(k)] : ! i [Golf(i)] : ! j [Next(i, j)] : ! c [Cnt(c)] : ! d [Succ(c, d)] : ~St(w, k, i, c) | ~assign(i, w, k) | St(w, k, j, d).
    ! w [Week(w)] : ! k [Grp(k)] : ! i [Golf(i)] : ! j [Next(i, j)] : ! c [Full(c)] : ~St(w, k, i, c) | ~assign(i, w, k).
    ! w [Week(w)] : ! k [Grp(k)] : ! i [Golf(i)] : ! j [Next(i, j)] : ! c [Cnt(c)] : ~St(w, k, i, c) | assign(i, w, k) | St(w, k, j, c).
    ! w [Week(w)] : ! k [Grp(k)] : ! l [Last(l)] : ! c [NotFull(c)] : ~St(w, k, l, c).
    ! a [Golf(a)] : ! b [Lt(a, b)] : ! w [Week(w)] : ! k [Grp(k)] : ~assign(a, w, k) | ~assign(b, w, k) | SameG(a, b, w).
    ! a [Golf(a)] : ! b [Lt(a, b)] : ! w [Week(w)] : ! w2 [Week(w2) & w ~= w2] : ~SameG(a, b, w) | ~SameG(a, b, w2).
}
"""


def structure(instance):
    gs = instance["group_size"]
    K = instance["n_groups"]
    W = instance["n_weeks"]
    G = K * gs
    return {
        "Golf": range(G),
        "Week": range(W),
        "Grp": range(K),
        "Pref": range(G + 1),
        "Cnt": range(gs + 1),
        "Start": [0],
        "Last": [G],
        "Full": [gs],
        "NotFull": range(gs),
        "Next": [(i, i + 1) for i in range(G)],
        "Succ": [(c, c + 1) for c in range(gs)],
        "Lt": [(a, b) for a in range(G) for b in range(a + 1, G)],
    }

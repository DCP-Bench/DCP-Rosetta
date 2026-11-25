# csplib_026_sports_tournament_scheduling: a FOX model for GroundFOX from DCP Rosetta.
#
# The problem is to schedule a tournament of \( n \) teams over \( n-1 \) weeks, with each
# week divided into \( n/2 \) periods, and each period divided into two slots. The first team
# in each slot plays at home, whilst the second plays the first team away. A tournament must
# satisfy the following three constraints: every team plays once a week; every team plays at
# most twice in the same period over the tournament; every team plays every other team.
#
# An example schedule for 8 teams is:
#
# | Week 1 | Week 2 | Week 3 | Week 4 | Week 5 | Week 6 | Week 7 |
# |---------|---------|---------|---------|---------|---------|---------| | 0 v 1 | 0 v 2 | 4
# v 7 | 3 v 6 | 3 v 7 | 1 v 5 | 2 v 4 | | 2 v 3 | 1 v 7 | 0 v 3 | 5 v 7 | 1 v 4 | 0 v 6 | 5 v
# 6 | | 4 v 5 | 3 v 5 | 1 v 6 | 0 v 4 | 2 v 6 | 2 v 7 | 0 v 7 | | 6 v 7 | 4 v 6 | 2 v 5 | 1 v
# 2 | 0 v 5 | 3 v 4 | 1 v 3 |
#
# Print the home and away schedules (home, away) as lists of lists, where, e.g. home[w][p] is
# the team playing home in week w and period p. The teams are numbered from 1 to n.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_026_sports_tournament_scheduling.json --check

# csplib_026_sports_tournament_scheduling: a FOX model for GroundFOX from DCP Rosetta.
#
# Schedule a round-robin tournament of n teams (n even) over n-1 weeks, n/2 periods per week,
# two slots per period (home and away). Every team plays once a week, at most twice in the same
# period over the tournament, and every pair of teams meets exactly once.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Wk/1 Pr/1 Tm/1 }
outvocabulary { home/3 away/3 pl/3 g/4 h/3 }
theory {
    ! w [Wk(w)] : ! p [Pr(p)] : ? t [Tm(t)] : home(w, p, t).
    ! w [Wk(w)] : ! p [Pr(p)] : ! t [Tm(t)] : ! u [Tm(u) & ~(t = u)] : ~home(w, p, t) | ~home(w, p, u).
    ! w [Wk(w)] : ! p [Pr(p)] : ? t [Tm(t)] : away(w, p, t).
    ! w [Wk(w)] : ! p [Pr(p)] : ! t [Tm(t)] : ! u [Tm(u) & ~(t = u)] : ~away(w, p, t) | ~away(w, p, u).
    ! w [Wk(w)] : ! p [Pr(p)] : ! t [Tm(t)] : ~home(w, p, t) | ~away(w, p, t).
    ! w [Wk(w)] : ! p [Pr(p)] : ! t [Tm(t)] : ~home(w, p, t) | pl(w, p, t).
    ! w [Wk(w)] : ! p [Pr(p)] : ! t [Tm(t)] : ~away(w, p, t) | pl(w, p, t).
    ! w [Wk(w)] : ! p [Pr(p)] : ! t [Tm(t)] : ~pl(w, p, t) | home(w, p, t) | away(w, p, t).
    ! w [Wk(w)] : ! t [Tm(t)] : ? p [Pr(p)] : pl(w, p, t).
    ! w [Wk(w)] : ! t [Tm(t)] : ! p [Pr(p)] : ! q [Pr(q) & ~(p = q)] : ~pl(w, p, t) | ~pl(w, q, t).
    ! p [Pr(p)] : ! t [Tm(t)] : ! w1 [Wk(w1)] : ! w2 [Wk(w2) & ~(w1 = w2)] : ! w3 [Wk(w3) & ~(w1 = w3) & ~(w2 = w3)] : ~pl(w1, p, t) | ~pl(w2, p, t) | ~pl(w3, p, t).
    ! w [Wk(w)] : ! p [Pr(p)] : ! t [Tm(t)] : ! u [Tm(u) & ~(t = u)] : ~g(w, p, t, u) | pl(w, p, t).
    ! w [Wk(w)] : ! p [Pr(p)] : ! t [Tm(t)] : ! u [Tm(u) & ~(t = u)] : ~g(w, p, t, u) | pl(w, p, u).
    ! w [Wk(w)] : ! p [Pr(p)] : ! t [Tm(t)] : ! u [Tm(u) & ~(t = u)] : ~pl(w, p, t) | ~pl(w, p, u) | g(w, p, t, u).
    ! t [Tm(t)] : ! u [Tm(u) & ~(t = u)] : ? w [Wk(w)] : h(w, t, u).
    ! w [Wk(w)] : ! t [Tm(t)] : ! u [Tm(u) & ~(t = u)] : ? p [Pr(p)] : g(w, p, t, u) | ~h(w, t, u).
    ! t [Tm(t)] : ! u [Tm(u) & ~(t = u)] : ! w [Wk(w)] : ! w2 [Wk(w2) & ~(w = w2)] : ! p [Pr(p)] : ! p2 [Pr(p2)] : ~g(w, p, t, u) | ~g(w2, p2, t, u).
    ! t [Tm(t)] : ! u [Tm(u) & ~(t = u)] : ! w [Wk(w)] : ! p [Pr(p)] : ! p2 [Pr(p2) & ~(p = p2)] : ~g(w, p, t, u) | ~g(w, p2, t, u).
}
"""


def structure(instance):
    n = instance["n_teams"]
    return {
        "domain": range(n + 1),
        "Wk": range(n - 1),
        "Pr": range(n // 2),
        "Tm": range(1, n + 1),
    }

# csplib_011_acc_basketball_schedule: a FOX model for GroundFOX from DCP Rosetta.
#
# The problem is finding a timetable for the 1997/98 Atlantic Coast Conference (ACC) in
# basketball.
#
# The 9 basketball teams in the tournament are Clemson (Clem), Duke (Duke), Florida State
# (FSU), Georgia Tech (GT), Maryland (UMD), North Carolina (UNC), North Carolina State (NCSt),
# Virginia (UVA), and Wake Forest (Wake). The problem is to determine a double round-robin
# schedule for these 9 teams subject to some additional constraints. In a double round-robin,
# each team plays each other, once at home, once away. The schedule is to be played over 18
# dates. The first and all subsequent odd dates are weekday fixtures. The second and all
# subsequent even dates are weekend fixtures. There are nine other sets of constraints.
#
# 1. Mirroring. The dates are grouped into pairs (r1, r2), such that each team will get to
# play against the same team in dates r1 and r2. Such a grouping is called a mirroring scheme.
# Nemhauser and Trick use the mirroring scheme {(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6,
# 15), (7, 16), (10, 17), (11, 18)}. A team playing at home on one date of a pair plays away
# on the other.
#
# 2. No Two Final Aways. No team can play away on both last dates.
#
# 3. Home/Away/Bye Pattern Constraints. No team may have more than two away matches in a row.
# No team may have more than two home matches in a row. No team may have more than three away
# matches or byes in a row. No team may have more than four home matches or byes in a row.
#
# 4. Weekend Pattern. Of the weekends, each team plays four at home, four away, and one bye.
#
# 5. First Weekends. Each team must have home matches or byes at least on two of the first
# five weekends.
#
# 6. Rival Matches. Every team except FSU has a traditional rival. The rival pairs are Duke-
# UNC, Clem-GT, NCSt-Wake, and UMD-UVA. In the last date, every team except FSU plays against
# its rival, unless it plays against FSU or has a bye.
#
# 7. Constrained Matches. The following pairings must occur at least once in dates 11 to 18:
# Wake-UNC, Wake-Duke, GT-UNC, and GT-Duke.
#
# 8. Opponent Sequence Constraints. No team plays in two consecutive dates away against UNC
# and Duke. No team plays in three consecutive dates against UNC, Duke and Wake (independent
# of home/away).
#
# 9. Other Constraints. UNC plays its rival Duke in the last date, and in date 11. UNC plays
# Clem in the second date. Duke has a bye in date 16. Wake does not play home in date 17. Wake
# has a bye in the first date. Clem, Duke, UMD and Wake do not play away in the last date.
# Clem, FSU, GT and Wake do not play away in the first date. Neither FSU nor NCSt have a bye
# in the last date. UNC does not have a bye in the first date.
#
# Print the match configuration (config) as a list of lists, where each inner list represents
# a day and contains the teams playing on that day; config[d,i] == j means that team i plays
# against team j on day d, and config[d,i] == i means that team i has a bye. Teams are
# numbered from 0 in the order listed above. Also print whether each team is playing home -0-,
# away -2-, or has a bye -1- (where); e.g. where[d,i] == 0 means that team i plays at home on
# day d.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_011_acc_basketball_schedule.json --check

"""csplib_011_acc_basketball_schedule: a FOX model for GroundFOX from DCP Rosetta.

Teams 0..8 (Clem, Duke, FSU, GT, UMD, UNC, NCSt, UVA, Wake), dates 0..17 (0-based).
config(d, i, v): team i on date d plays team v (v = i is a bye).
where(d, i, w): w = 0 home, 1 bye, 2 away.
HM(d, i, j): team i hosts team j on date d (defines the double round robin).
CH / CA: deterministic counters of home / away weekend games per team.
Odd 0-based dates are weekends. Data relations (windows, mirror pairs, rivals, counts,
the fixed pins of rule 9 as allowed tuples) come from the structure; the constraints are
quantified sentences over them.
"""
from itertools import combinations

FOX = """
invocabulary { Team/1 Date/1 Next/2 Tri/3 W4/4 W5/5 Wkend/1 Wkday/1 Count/1 Succ/2 Zero/1 NotFour/1 First/1 Last/1 Fw/1 Fw4/4 Rival/2 FSU/1 CPair/2 Late/1 Mir/2 Wv/1 Trio/1 Must/3 Avoid/3 }
outvocabulary { config/3 where/3 HM/3 CH/3 CA/3 }
theory {
    ! d [Date(d)] : ! i [Team(i)] : ? v [Team(v)] : config(d, i, v).
    ! d [Date(d)] : ! i [Team(i)] : ! v [Team(v)] : ! w [Team(w) & v ~= w] : ~config(d, i, v) | ~config(d, i, w).
    ! d [Date(d)] : ! i [Team(i)] : ? w [Wv(w)] : where(d, i, w).
    ! d [Date(d)] : ! i [Team(i)] : ! v [Wv(v)] : ! w [Wv(w) & v ~= w] : ~where(d, i, v) | ~where(d, i, w).

    ! d [Date(d)] : ! i [Team(i)] : ! j [Team(j)] : ~HM(d, i, j) | config(d, i, j).
    ! d [Date(d)] : ! i [Team(i)] : ! j [Team(j)] : ~HM(d, i, j) | where(d, i, 0).
    ! d [Date(d)] : ! i [Team(i)] : ! j [Team(j)] : ~HM(d, i, j) | where(d, j, 2).
    ! d [Date(d)] : ! i [Team(i)] : ! j [Team(j) & i ~= j] : ~config(d, i, j) | HM(d, i, j) | HM(d, j, i).
    ! d [Date(d)] : ! i [Team(i)] : ? j [Team(j)] : HM(d, i, j) | ~where(d, i, 0).
    ! d [Date(d)] : ! i [Team(i)] : ? j [Team(j)] : HM(d, j, i) | ~where(d, i, 2).
    ! d [Date(d)] : ! i [Team(i)] : ~where(d, i, 1) | config(d, i, i).
    ! d [Date(d)] : ! i [Team(i)] : ~config(d, i, i) | where(d, i, 1).
    ! d [Date(d)] : ! i [Team(i)] : ! j [Team(j)] : ~HM(d, i, j) | ~HM(d, j, i).
    ! i [Team(i)] : ! j [Team(j) & i ~= j] : ? d [Date(d)] : HM(d, i, j).
    ! i [Team(i)] : ! j [Team(j) & i ~= j] : ! d [Date(d)] : ! e [Date(e) & d ~= e] : ~HM(d, i, j) | ~HM(e, i, j).

    ! d [Date(d)] : ! s [Mir(d, s)] : ! i [Team(i)] : ! v [Team(v)] : ~config(d, i, v) | config(s, i, v).
    ! d [Date(d)] : ! s [Mir(d, s)] : ! i [Team(i)] : ~where(d, i, 0) | where(s, i, 2).
    ! d [Date(d)] : ! s [Mir(d, s)] : ! i [Team(i)] : ~where(d, i, 2) | where(s, i, 0).

    ! i [Team(i)] : ! d [Date(d)] : ! e [Date(e)] : ! f [Tri(d, e, f)] : ~where(d, i, 2) | ~where(e, i, 2) | ~where(f, i, 2).
    ! i [Team(i)] : ! d [Date(d)] : ! e [Date(e)] : ! f [Tri(d, e, f)] : ~where(d, i, 0) | ~where(e, i, 0) | ~where(f, i, 0).
    ! i [Team(i)] : ! d [Date(d)] : ! e [Date(e)] : ! f [Date(f)] : ! g [W4(d, e, f, g)] : where(d, i, 0) | where(e, i, 0) | where(f, i, 0) | where(g, i, 0).
    ! i [Team(i)] : ! d [Date(d)] : ! e [Date(e)] : ! f [Date(f)] : ! g [Date(g)] : ! h [W5(d, e, f, g, h)] : where(d, i, 2) | where(e, i, 2) | where(f, i, 2) | where(g, i, 2) | where(h, i, 2).

    ! i [Team(i)] : ! a [Fw(a)] : ! b [Fw(b)] : ! c [Fw(c)] : ! d [Fw4(a, b, c, d)] : ~where(a, i, 2) | ~where(b, i, 2) | ~where(c, i, 2) | ~where(d, i, 2).

    ! i [Team(i)] : ! d [First(d)] : ! c [Zero(c)] : CH(i, d, c).
    ! i [Team(i)] : ! d [First(d)] : ! c [Zero(c)] : CA(i, d, c).
    ! i [Team(i)] : ! d [Date(d)] : ! e [Next(d, e) & Wkday(e)] : ! c [Count(c)] : ~CH(i, d, c) | CH(i, e, c).
    ! i [Team(i)] : ! d [Date(d)] : ! e [Next(d, e) & Wkday(e)] : ! c [Count(c)] : ~CA(i, d, c) | CA(i, e, c).
    ! i [Team(i)] : ! d [Date(d)] : ! e [Next(d, e) & Wkend(e)] : ! c [Count(c)] : ! k [Succ(c, k)] : ~CH(i, d, c) | ~where(e, i, 0) | CH(i, e, k).
    ! i [Team(i)] : ! d [Date(d)] : ! e [Next(d, e) & Wkend(e)] : ! c [Count(c)] : ~CH(i, d, c) | where(e, i, 0) | CH(i, e, c).
    ! i [Team(i)] : ! d [Date(d)] : ! e [Next(d, e) & Wkend(e)] : ! c [Count(c)] : ! k [Succ(c, k)] : ~CA(i, d, c) | ~where(e, i, 2) | CA(i, e, k).
    ! i [Team(i)] : ! d [Date(d)] : ! e [Next(d, e) & Wkend(e)] : ! c [Count(c)] : ~CA(i, d, c) | where(e, i, 2) | CA(i, e, c).
    ! i [Team(i)] : ! l [Last(l)] : ! c [NotFour(c)] : ~CH(i, l, c).
    ! i [Team(i)] : ! l [Last(l)] : ! c [NotFour(c)] : ~CA(i, l, c).

    ! i [Team(i)] : ~where(16, i, 2) | ~where(17, i, 2).
    ! d [Last(d)] : ! i [Team(i)] : ! r [Rival(i, r)] : ! f [FSU(f)] : config(d, i, r) | config(d, i, f) | config(d, i, i).
    ! a [Team(a)] : ! b [CPair(a, b)] : ? d [Late(d)] : config(d, a, b).

    ! i [Team(i)] : ! d [Date(d)] : ! e [Next(d, e)] : ~config(d, i, 5) | ~where(d, i, 2) | ~config(e, i, 1) | ~where(e, i, 2).
    ! i [Team(i)] : ! d [Date(d)] : ! e [Next(d, e)] : ~config(d, i, 1) | ~where(d, i, 2) | ~config(e, i, 5) | ~where(e, i, 2).

    ! i [Team(i)] : ! d [Date(d)] : ! e [Date(e)] : ! f [Tri(d, e, f)] : ! a [Trio(a)] : ! b [Trio(b) & a ~= b] : ! c [Trio(c) & a ~= c & b ~= c] : ~config(d, i, a) | ~config(e, i, b) | ~config(f, i, c).

    ! d [Date(d)] : ! i [Team(i)] : ! v [Must(d, i, v)] : config(d, i, v).
    ! d [Date(d)] : ! i [Team(i)] : ! w [Avoid(d, i, w)] : ~where(d, i, w).
}
"""

MIRROR_PAIRS = [(0, 7), (1, 8), (2, 11), (3, 12), (4, 13), (5, 14), (6, 15), (9, 16), (10, 17)]

# Rule 9 pins as allowed tuples (0-based): config(d, i, v) must hold; where(d, i, w) must not.
MUST = [(17, 5, 1), (10, 5, 1), (1, 5, 0), (15, 1, 1), (0, 8, 8)]
AVOID = [(16, 8, 0), (17, 0, 2), (17, 1, 2), (17, 4, 2), (17, 8, 2), (0, 0, 2), (0, 2, 2),
         (0, 3, 2), (0, 8, 2), (17, 2, 1), (17, 6, 1), (0, 5, 1)]


def structure(instance):
    n_days = instance["n_days"]
    n_teams = instance["n_teams"]
    days = list(range(n_days))
    weekend = [d for d in days if d % 2 == 1]
    weekday = [d for d in days if d % 2 == 0]
    fw = weekend[:5]
    return {
        "Team": range(n_teams),
        "Date": days,
        "Next": [(d, d + 1) for d in range(n_days - 1)],
        "Tri": [(d, d + 1, d + 2) for d in range(n_days - 2)],
        "W4": [(d, d + 1, d + 2, d + 3) for d in range(n_days - 3)],
        "W5": [(d, d + 1, d + 2, d + 3, d + 4) for d in range(n_days - 4)],
        "Wkend": weekend,
        "Wkday": weekday,
        "Count": range(10),
        "Succ": [(c, c + 1) for c in range(9)],
        "Zero": [0],
        "NotFour": [c for c in range(10) if c != 4],
        "First": [0],
        "Last": [n_days - 1],
        "Fw": fw,
        "Fw4": list(combinations(fw, 4)),
        "Rival": [(1, 5), (5, 1), (0, 3), (3, 0), (6, 8), (8, 6), (4, 7), (7, 4)],
        "FSU": [2],
        "CPair": [(8, 5), (8, 1), (3, 5), (3, 1)],
        "Late": [d for d in days if d >= 10],
        "Mir": MIRROR_PAIRS + [(b, a) for a, b in MIRROR_PAIRS],
        "Wv": [0, 1, 2],
        "Trio": [1, 5, 8],
        "Must": MUST,
        "Avoid": AVOID,
    }

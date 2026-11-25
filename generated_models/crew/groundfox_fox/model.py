# crew: a FOX model for GroundFOX from DCP Rosetta.
#
# Assign flight attendants to flights. Each flight needs a certain number of cabin crew, and
# they have to speak certain languages.
#
# `attributes[p]` describes person p as five 0/1 values: steward, hostess, speaks French,
# speaks Spanish, speaks German. `required_crew[f]` describes flight f as six numbers: the
# number of cabin crew, then the numbers of stewards, hostesses, French speakers, Spanish
# speakers and German speakers needed. A flight has exactly that number of cabin crew, and at
# least the required number of each of the others; one person can count towards several of
# them.
#
# Every cabin crew member has at least two flights off after an attended flight, so nobody
# attends more than one of any three consecutive flights.
#
# Print whether for each flight a person is assigned to it (crew) as a list of lists of 0/1
# values, where crew[f][p] is 1 if person p is assigned to flight f, and 0 otherwise.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py crew.json --check

# crew: a FOX model for GroundFOX from DCP Rosetta.
#
# crew[f][p] is 1 iff person p is assigned to flight f. Per flight, a layered counter
# over the persons tracks how many assigned persons count towards each requirement
# (kind 0: all cabin crew; kinds 1..5: stewards, hostesses, French, Spanish, German).
# cnt(f, a, p, k): after the persons before p, k assigned persons count for kind a.
# The forward rules force the true counts; the last layer must satisfy the requirement.

FOX = """
invocabulary { Flight/1 Person/1 Pos/1 Count/1 Kind/1 Bit/1 Succ/2 Inc/2 Last/1 Yes/2 Ok/3 Near/2 }
outvocabulary { crew/3 cnt/4 }
theory {
    ! f [Flight(f)] : ! p [Person(p)] : ? b [Bit(b)] : crew(f, p, b).
    ! f [Flight(f)] : ! p [Person(p)] : ! b [Bit(b)] : ! c [Bit(c) & b ~= c] : ~crew(f, p, b) | ~crew(f, p, c).
    ! f [Flight(f)] : ! a [Kind(a)] : cnt(f, a, 0, 0).
    ! f [Flight(f)] : ! a [Kind(a)] : ! p [Last(p)] : ! k [Count(k) & ~Ok(f, a, k)] : ~cnt(f, a, p, k).
    ! f [Flight(f)] : ! a [Kind(a)] : ! p [Person(p) & Yes(a, p)] : ! q [Succ(p, q)] : ! k [Count(k)] : ! k2 [Inc(k, k2)] : ~cnt(f, a, p, k) | ~crew(f, p, 1) | cnt(f, a, q, k2).
    ! f [Flight(f)] : ! a [Kind(a)] : ! p [Person(p) & Yes(a, p)] : ! q [Succ(p, q)] : ! k [Count(k)] : ~cnt(f, a, p, k) | ~crew(f, p, 0) | cnt(f, a, q, k).
    ! f [Flight(f)] : ! a [Kind(a)] : ! p [Person(p) & ~Yes(a, p)] : ! q [Succ(p, q)] : ! k [Count(k)] : ~cnt(f, a, p, k) | cnt(f, a, q, k).
    ! p [Person(p)] : ! f [Flight(f)] : ! g [Near(f, g)] : ~crew(f, p, 1) | ~crew(g, p, 1).
}
"""


def structure(instance):
    attrs = instance["attributes"]
    req = instance["required_crew"]
    n_flights = len(req)
    n_people = len(attrs)
    yes = [(0, p) for p in range(n_people)]
    yes += [(a + 1, p) for p in range(n_people) for a in range(5) if attrs[p][a] == 1]
    ok = []
    for f in range(n_flights):
        r = req[f]
        for k in range(n_people + 1):
            if k == r[0]:
                ok.append((f, 0, k))
            for a in range(1, 6):
                if k >= r[a]:
                    ok.append((f, a, k))
    return {
        "Flight": list(range(n_flights)),
        "Person": list(range(n_people)),
        "Pos": list(range(n_people + 1)),
        "Count": list(range(n_people + 1)),
        "Kind": list(range(6)),
        "Bit": [0, 1],
        "Succ": [(p, p + 1) for p in range(n_people)],
        "Inc": [(k, k + 1) for k in range(n_people)],
        "Last": [n_people],
        "Yes": yes,
        "Ok": ok,
        "Near": [(f, g) for f in range(n_flights) for g in range(n_flights)
                 if 0 < abs(f - g) <= 2],
    }

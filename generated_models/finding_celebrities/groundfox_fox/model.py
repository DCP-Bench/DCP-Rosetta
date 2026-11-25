# finding_celebrities: a FOX model for GroundFOX from DCP Rosetta.
#
# Given a list of people at a party and for each person the list of people they know at the
# party, we want to find the celebrities at the party. A celebrity is a person that everybody
# at the party knows but that only knows other celebrities. At least one celebrity is present
# at the party.
#
# Print whether each person is a celebrity or not (celebrities) as 0/1 values, with the same
# order as the input data.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py finding_celebrities.json --check

FOX = """
invocabulary { Per/1 Bool/1 Ne/2 Kn/2 }
outvocabulary { celebrities/2 }
theory {
    ! p [Per(p)] : ? b [Bool(b)] : celebrities(p, b).
    ! p [Per(p)] : ! b [Bool(b)] : ! c [Bool(c) & b ~= c] : ~celebrities(p, b) | ~celebrities(p, c).
    ! p [Per(p)] : ! x [Ne(x, p)] : ~celebrities(p, 1).
    ! p [Per(p)] : ! q [Kn(p, q)] : ~celebrities(p, 1) | celebrities(q, 1).
    ? p [Per(p)] : celebrities(p, 1).
}
"""


def structure(instance):
    g = instance["graph"]
    n = len(g)
    persons = list(range(n))
    # Ne: x does not know p (x != p), so p cannot be a celebrity.
    not_known = [(x, p) for p in persons for x in persons if x != p and g[x][p] == 0]
    # Kn: p knows q (q != p), so if p is a celebrity then q must be one.
    knows = [(p, q) for p in persons for q in persons if p != q and g[p][q] == 1]
    return {
        "domain": list(range(max(n, 2) + 1)),
        "Per": persons,
        "Bool": [0, 1],
        "Ne": not_known,
        "Kn": knows,
    }

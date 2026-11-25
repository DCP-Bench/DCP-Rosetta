# ages_of_the_sons: a FOX model for GroundFOX from DCP Rosetta.
#
# An old man asked a mathematician to guess the ages of his three sons.
#
# Old man said: "The product of their ages is 36." Mathematician said: "I need more
# information."
#
# Old man said:"Over there you can see a building. The sum of their ages equals the number of
# the windows in that building." After a short while the mathematician said: "I need more
# information."
#
# Old man said: "The oldest son has blue eyes." Mathematician said: "I got it."
#
# What are the ages of the three sons of the old man?
#
# Print the ages of the sons (A1, A2, A3) starting from the oldest.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py ages_of_the_sons.json --check

# ages_of_the_sons: a FOX model for GroundFOX from DCP Rosetta.
#
# An old man has three sons whose ages multiply to 36. The sum of the ages equals the number of
# windows of a building; the mathematician needs more information twice, and after learning that
# the oldest son has blue eyes he knows the ages. Print the ages A1, A2, A3 starting from the oldest.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Val/1 Tr/3 SS/6 UO/3 }
outvocabulary { A1/1 A2/1 A3/1 }
theory {
    ? a [Val(a)] : A1(a).
    ! a [Val(a)] : ! b [Val(b) & a ~= b] : ~A1(a) | ~A1(b).
    ? a [Val(a)] : A2(a).
    ! a [Val(a)] : ! b [Val(b) & a ~= b] : ~A2(a) | ~A2(b).
    ? a [Val(a)] : A3(a).
    ! a [Val(a)] : ! b [Val(b) & a ~= b] : ~A3(a) | ~A3(b).
    ! a [Val(a)] : ! b [Val(b)] : ! c [Val(c) & ~Tr(a,b,c)] : ~A1(a) | ~A2(b) | ~A3(c).
    ! a [Val(a)] : ! b [Val(b)] : ! c [Val(c) & ~UO(a,b,c)] : ~A1(a) | ~A2(b) | ~A3(c).
    ! a [Val(a)] : ! b [Val(b)] : ! c [Val(c)] : ~A1(a) | ~A2(b) | ~A3(c) | ? d [Val(d)] : ? e [Val(e)] : ? f [SS(a,b,c,d,e,f)] : Tr(d,e,f).
    ! a [Val(a)] : ! b [Val(b)] : ! c [Val(c)] : ! d [Val(d)] : ! e [Val(e)] : ! f [SS(a,b,c,d,e,f) & UO(d,e,f)] : ~A1(a) | ~A2(b) | ~A3(c).
}
"""


def structure(instance):
    # Ages are positive integers whose product is the constant 36; triples are listed oldest first.
    prod = 36
    cands = []
    for a in range(1, prod + 1):
        for b in range(1, a + 1):
            for c in range(1, b + 1):
                if a * b * c == prod:
                    cands.append((a, b, c))
    vals = sorted({x for t in cands for x in t})
    # Pairs of distinct candidate triples with the same sum (the windows statement).
    ss = [t + u for t in cands for u in cands if t != u and sum(t) == sum(u)]
    # Unique oldest son: the eldest is strictly older than the second.
    uo = [t for t in cands if t[0] > t[1]]
    return {"Val": vals, "Tr": cands, "SS": ss, "UO": uo}

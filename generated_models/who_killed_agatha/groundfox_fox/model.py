# who_killed_agatha: a FOX model for GroundFOX from DCP Rosetta.
#
# Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler, and Charles live in
# Dreadsbury Mansion, and are the only ones to live there. A killer always hates, and is no
# richer than his victim. Charles hates noone that Agatha hates. Agatha hates everybody except
# the butler. The butler hates everyone not richer than Aunt Agatha. The butler hates everyone
# whom Agatha hates. Noone hates everyone. Who killed Agatha?
#
# Print the 0-based index of the killer (killer).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py who_killed_agatha.json --check

# who_killed_agatha: a FOX model for GroundFOX from DCP Rosetta.
#
# Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler and Charles live there
# and are the only ones to live there. A killer always hates, and is no richer than his victim.
# Charles hates no one that Agatha hates. Agatha hates everybody except the butler. The butler
# hates everyone not richer than Aunt Agatha, and everyone whom Agatha hates. No one hates
# everyone. Who killed Agatha? Print the 0-based index of the killer (killer).
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

# hates/2 and richer/2 are auxiliary relations over the three residents.
FOX = """
invocabulary { P/1 Ag/1 Bu/1 Ch/1 }
outvocabulary { killer/1 hates/2 richer/2 }
theory {
    ? x [P(x)] : killer(x).
    ! x [P(x)] : ! y [P(y) & x ~= y] : ~killer(x) | ~killer(y).

    ! x [P(x)] : ! a [Ag(a)] : ~killer(x) | hates(x,a).
    ! x [P(x)] : ! a [Ag(a)] : ~killer(x) | ~richer(x,a).

    ! a [Ag(a)] : ! y [P(y) & ~Bu(y)] : hates(a,y).
    ! a [Ag(a)] : ! y [Bu(y)] : ~hates(a,y).

    ! a [Ag(a)] : ! c [Ch(c)] : ! y [P(y)] : ~hates(a,y) | ~hates(c,y).

    ! b [Bu(b)] : ! a [Ag(a)] : ! y [P(y)] : richer(y,a) | hates(b,y).
    ! b [Bu(b)] : ! a [Ag(a)] : ! y [P(y)] : ~hates(a,y) | hates(b,y).

    ! x [P(x)] : ? y [P(y)] : ~hates(x,y).
}
"""


def structure(instance):
    names = instance["names"]
    lower = [str(n).lower() for n in names]

    def find(word):
        hits = [i for i, n in enumerate(lower) if word in n]
        return hits

    persons = list(range(len(names)))
    return {
        "domain": persons,
        "P": persons,
        "Ag": find("agatha"),
        "Bu": find("butler"),
        "Ch": find("charles"),
    }

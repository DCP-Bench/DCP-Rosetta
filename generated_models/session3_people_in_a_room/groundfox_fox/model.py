# session3_people_in_a_room: a FOX model for GroundFOX from DCP Rosetta.
#
# There are 13 people. 4 of them are male. They randomly enter a room one at a time. Find a
# way that the males and females enter so that the ratio of females to males in the room at
# any one time is no greater than 7/3?
#
# Print the sequence of people entering the room (sequence), as a list of booleans, where 0
# represents male and 1 represents female.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_people_in_a_room.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session3_people_in_a_room.json --check

FOX = """
invocabulary { Pos/1 Bit/1 Ks/1 Fv/1 Step/2 Succ/2 Bad/2 Last/1 Target/1 }
outvocabulary { sequence/2 S/2 }
theory {
    ! i [Pos(i)] : ? b [Bit(b)] : sequence(i, b).
    ! i [Pos(i)] : ! b [Bit(b)] : ! c [Bit(c) & b ~= c] : ~sequence(i, b) | ~sequence(i, c).
    ! u [u = 0] : S(0, 0).
    ! k [Ks(k)] : ? f [Fv(f)] : S(k, f).
    ! k [Ks(k)] : ! f [Fv(f)] : ! g [Fv(g) & f ~= g] : ~S(k, f) | ~S(k, g).
    ! k [Ks(k)] : ! f [Bad(k, f)] : ~S(k, f).
    ! k [Ks(k)] : ! j [Step(k, j)] : ! f [Fv(f)] : ! g [Succ(f, g)] : ~S(k, f) | ~sequence(k, 1) | S(j, g).
    ! k [Ks(k)] : ! j [Step(k, j)] : ! f [Fv(f)] : ~S(k, f) | ~sequence(k, 0) | S(j, f).
    ! k [Last(k)] : ! f [Fv(f) & ~Target(f)] : ~S(k, f).
}
"""

FLAGS = []


def structure(instance):
    n = 13          # people
    females = 9     # 13 people, 4 males
    size = n + 1
    # Prefix of length k with f females and k - f males: f/m <= 7/3  <=>  10 f <= 7 k.
    bad = [(k, f) for k in range(size) for f in range(size) if 10 * f > 7 * k]
    return {
        "domain": range(size + 1),
        "Pos": range(n),
        "Bit": [0, 1],
        "Ks": range(size),
        "Fv": range(size),
        "Step": [(k, k + 1) for k in range(n)],
        "Succ": [(f, f + 1) for f in range(size - 1)],
        "Bad": bad,
        "Last": [n],
        "Target": [females],
    }

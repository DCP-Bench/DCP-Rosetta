# huey_dewey_louie: a FOX model for GroundFOX from DCP Rosetta.
#
# Huey, Dewey and Louie are being questioned by their uncle. These are the statements they
# make: - Huey: Dewey and Louie have an equal share in it; if one is guilty, so is the other.
# - Dewey: If Huey is guilty, then so am I. - Louie: Dewey and I are not both guilty.
#
# Their uncle, knowing that they are cub scouts, realises that they cannot tell a lie. Has he
# got sufficient information to decide who (if any) are guilty?
#
# Print whether Huey, Dewey, and Louie (huey, dewey, louie) are guilty or not.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/huey_dewey_louie.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py huey_dewey_louie.json --check

# huey_dewey_louie: a FOX model for GroundFOX from DCP Rosetta.
#
# Huey, Dewey and Louie cannot lie, so each statement is true:
#   Huey:  Dewey and Louie are both guilty or both innocent.
#   Dewey: if Huey is guilty, then Dewey is guilty.
#   Louie: Dewey and Louie are not both guilty.
# Output whether each of huey, dewey, louie is guilty (1) or not (0).

FOX = """
invocabulary { Bit/1 One/1 }
outvocabulary { huey/1 dewey/1 louie/1 }
theory {
    ? b [Bit(b)] : huey(b).
    ! b [Bit(b)] : ! c [Bit(c) & b ~= c] : ~huey(b) | ~huey(c).
    ? b [Bit(b)] : dewey(b).
    ! b [Bit(b)] : ! c [Bit(c) & b ~= c] : ~dewey(b) | ~dewey(c).
    ? b [Bit(b)] : louie(b).
    ! b [Bit(b)] : ! c [Bit(c) & b ~= c] : ~louie(b) | ~louie(c).
    ! x [One(x)] : ~dewey(x) | louie(x).
    ! x [One(x)] : ~louie(x) | dewey(x).
    ! x [One(x)] : ~huey(x) | dewey(x).
    ! x [One(x)] : ~dewey(x) | ~louie(x).
}
"""


def structure(instance):
    return {
        "domain": [0, 1],
        "Bit": [0, 1],
        "One": [1],
    }

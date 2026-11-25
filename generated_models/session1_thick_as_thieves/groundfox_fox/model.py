# session1_thick_as_thieves: a FOX model for GroundFOX from DCP Rosetta.
#
# Following a robbery at Sparkles the Jeweller’s, Inspector Korner of the Yard interviewed six
# of the usual suspects. He knew that the getaway car had been barely big enough to hold two,
# so he reckoned that at least four of them were innocent - but which ones? He also supposed
# that the innocent ones would tell the truth, while the guilty one or ones would lie. What
# they actually said was: - ARTIE: "It wasn't me." - BILL: "Crackitt was in it up to his
# neck." - CRACKITT: "No I wasn't." - DODGY: "If Crackitt did it, Bill did it with him." -
# EDGY: "Nobody did it alone." - FINGERS: "That’s right: it was Artie and Dodgy together." If
# the good inspector’s suppositions were correct, who is guilty?
#
# Print whether each suspect is guilty or not (artie, bill, crackitt, dodgy, edgy, fingers).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session1_thick_as_thieves.json --check

# session1_thick_as_thieves: a FOX model for GroundFOX from DCP Rosetta.
#
# Six suspects (artie 0, bill 1, crackitt 2, dodgy 3, edgy 4, fingers 5). Each suspect's
# guilt is g(i, 1); g(i, 0) means innocent. Each named output takes the same value.
# An innocent suspect tells the truth and a guilty one lies, so guilty(i) <=> not S_i,
# where S_i is the truth of the statement. At most two are guilty (the car held two).
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Suspect/1 Bool/1 }
outvocabulary { artie/1 bill/1 crackitt/1 dodgy/1 edgy/1 fingers/1 g/2 other/1 both/1 }
theory {
    ! i [Suspect(i)] : ? v [Bool(v)] : g(i, v).
    ! i [Suspect(i)] : ! v [Bool(v)] : ! w [Bool(w) & v ~= w] : ~g(i, v) | ~g(i, w).

    ! v [Bool(v)] : ~artie(v) | g(0, v).
    ! v [Bool(v)] : ~g(0, v) | artie(v).
    ! v [Bool(v)] : ~bill(v) | g(1, v).
    ! v [Bool(v)] : ~g(1, v) | bill(v).
    ! v [Bool(v)] : ~crackitt(v) | g(2, v).
    ! v [Bool(v)] : ~g(2, v) | crackitt(v).
    ! v [Bool(v)] : ~dodgy(v) | g(3, v).
    ! v [Bool(v)] : ~g(3, v) | dodgy(v).
    ! v [Bool(v)] : ~edgy(v) | g(4, v).
    ! v [Bool(v)] : ~g(4, v) | edgy(v).
    ! v [Bool(v)] : ~fingers(v) | g(5, v).
    ! v [Bool(v)] : ~g(5, v) | fingers(v).

    ! i [Suspect(i)] : ! j [Suspect(j) & i ~= j] : ! k [Suspect(k) & i ~= k & j ~= k] : ~g(i, 1) | ~g(j, 1) | ~g(k, 1).

    ! i [Suspect(i)] : ? j [Suspect(j) & i ~= j] : g(j, 1) | ~other(i).
    ! i [Suspect(i)] : ! j [Suspect(j) & i ~= j] : ~g(j, 1) | other(i).
    ! i [Suspect(i)] : ~both(i) | g(i, 1).
    ! i [Suspect(i)] : ~both(i) | other(i).
    ! i [Suspect(i)] : ~g(i, 1) | ~other(i) | both(i).

    ! u [Bool(u) & u = 1] : g(1, 1) | g(2, 1).
    ! u [Bool(u) & u = 1] : ~g(1, 1) | ~g(2, 1).
    ! u [Bool(u) & u = 1] : ~g(3, 1) | g(2, 1).
    ! u [Bool(u) & u = 1] : ~g(3, 1) | ~g(1, 1).
    ! u [Bool(u) & u = 1] : g(3, 1) | ~g(2, 1) | g(1, 1).
    ! u [Bool(u) & u = 1] : ~g(5, 1) | ~g(0, 1) | ~g(3, 1).
    ! u [Bool(u) & u = 1] : g(5, 1) | g(0, 1).
    ! u [Bool(u) & u = 1] : g(5, 1) | g(3, 1).

    ? i [Suspect(i)] : both(i) | g(4, 1).
    ! i [Suspect(i)] : ~both(i) | ~g(4, 1).
}
"""


def structure(instance):
    return {"Suspect": range(6), "Bool": [0, 1]}

# big_bang2: a FOX model for GroundFOX from DCP Rosetta.
#
# Nontransitive dice: The idea is to create a set of five dice such that the dominance
# relationships between the dice is isomorphic to the corresponding relationships in the game
# Rock-Paper-Scissors extended by the choices Lizard and Spock. Each choice beats two other
# choices and is beaten by two other choices. In particular, we have the following ten 'beats'
# relationships
#
# 1: Rock(1) crushes Scissors(3) 2: Rock(1) crushes Lizard(4) 3: Paper(2) covers Rock(1) 4:
# Paper(2) disproves Spock(5) 5: Scissors(3) cuts Paper(2) 6: Scissors(3) decapitate Lizard(4)
# 7: Lizard(4) eats Paper(2) 8: Lizard(4) poisons Spock(5) 9: Spock(5) vaporizes Rock(1) 10:
# Spock(5) smashes Scissors(3)
#
# Each die has six integer-valued faces, and each face value must be between 1 and 12
# inclusive. Face values may repeat, both within a die and across dice. We define the 'beats'
# relationship between two dice to be the following: A has a strictly larger face value than
# die B in more than half of all possible pairs of faces.
#
# Print the dice (dice) as a list of lists where each sublist is a die; row 0 is Rock, row 1
# is Paper, row 2 is Scissors, row 3 is Lizard, and row 4 is Spock.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/big_bang2.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py big_bang2.json --check

NDICE = 5
NFACE = 6
NVAL = 12
NSTEP = NFACE * NFACE  # face pairs (i, j), enumerated as steps 0..35; final state is 36
PAIRS = [(i, j) for i in range(NFACE) for j in range(NFACE)]
# Ten 'beats' facts, dice 0-based: Rock 0, Paper 1, Scissors 2, Lizard 3, Spock 4.
BEATS = [(0, 2), (0, 3), (1, 0), (1, 4), (2, 1), (2, 3), (3, 1), (3, 4), (4, 0), (4, 2)]

FOX = """
invocabulary { Dice/1 Face/1 Val/1 Cnt/1 Pos/1 Zero/1 First/1 Final/1 Low/1 Hi/1 Nxt/2 Succ/2 Diff/2 Beats/2 Gt/2 PairOf/3 }
outvocabulary { dice/3 g/4 S/4 }
theory {
    ! d [Dice(d)] : ! i [Face(i)] : ? v [Val(v)] : dice(d, i, v).
    ! d [Dice(d)] : ! i [Face(i)] : ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~dice(d, i, v) | ~dice(d, i, w).

    ! d [Dice(d)] : ! e [Diff(d, e)] : ! i [Face(i)] : ! j [Face(j)] : ! v [Val(v)] : ! w [Val(w) & Gt(v, w)] : ~dice(d, i, v) | ~dice(e, j, w) | g(d, e, i, j).
    ! d [Dice(d)] : ! e [Diff(d, e)] : ! i [Face(i)] : ! j [Face(j)] : ! v [Val(v)] : ! w [Val(w) & ~Gt(v, w)] : ~dice(d, i, v) | ~dice(e, j, w) | ~g(d, e, i, j).

    ! d [Dice(d)] : ! e [Diff(d, e)] : ! p [First(p)] : ! s [Zero(s)] : S(d, e, p, s).
    ! d [Dice(d)] : ! e [Diff(d, e)] : ! p [Pos(p)] : ! q [Nxt(p, q)] : ! i [Face(i)] : ! j [Face(j) & PairOf(p, i, j)] : ! s [Cnt(s)] : ! t [Succ(s, t)] : ~S(d, e, p, s) | ~g(d, e, i, j) | S(d, e, q, t).
    ! d [Dice(d)] : ! e [Diff(d, e)] : ! p [Pos(p)] : ! q [Nxt(p, q)] : ! i [Face(i)] : ! j [Face(j) & PairOf(p, i, j)] : ! s [Cnt(s)] : ~S(d, e, p, s) | g(d, e, i, j) | S(d, e, q, s).

    ! d [Dice(d)] : ! e [Beats(d, e)] : ! p [Final(p)] : ! s [Low(s)] : ~S(d, e, p, s).
    ! d [Dice(d)] : ! e [Diff(d, e) & ~Beats(d, e)] : ! p [Final(p)] : ! s [Hi(s)] : ~S(d, e, p, s).
}
"""


def structure(instance):
    return {
        "Dice": list(range(NDICE)),
        "Face": list(range(NFACE)),
        "Val": list(range(1, NVAL + 1)),
        "Cnt": list(range(NSTEP + 1)),
        "Zero": [0],
        "Pos": list(range(NSTEP)),
        "First": [0],
        "Final": [NSTEP],
        "Low": list(range(0, 19)),
        "Hi": list(range(19, NSTEP + 1)),
        "Nxt": [(p, p + 1) for p in range(NSTEP)],
        "Succ": [(s, s + 1) for s in range(NSTEP)],
        "Diff": [(d, e) for d in range(NDICE) for e in range(NDICE) if d != e],
        "Beats": BEATS,
        "Gt": [(v, w) for v in range(1, NVAL + 1) for w in range(1, NVAL + 1) if v > w],
        "PairOf": [(p, i, j) for p, (i, j) in enumerate(PAIRS)],
    }

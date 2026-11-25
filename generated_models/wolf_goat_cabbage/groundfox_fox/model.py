# wolf_goat_cabbage: a FOX model for GroundFOX from DCP Rosetta.
#
# The wolf, goat and cabbage problem is a river crossing puzzle. It dates back to at least the
# 9th century, and has entered the folklore of several cultures.
#
# The story: A farmer with a wolf, a goat, and a cabbage must cross a river by boat. The boat
# can carry only the farmer and a single item. If left unattended together, the wolf would eat
# the goat, or the goat would eat the cabbage. How can they cross the river without anything
# being eaten?
#
# The crossing takes the given number of stages. At the first stage everything is on the
# starting shore, at the last stage everything is on the destination shore, and the boat, with
# the farmer, changes shore from each stage to the next.
#
# Print whether the wolf, goat, cabbage, and boat are on the destination shore -1- or the
# starting shore -0- at each stage (wolf_pos, goat_pos, cabbage_pos, boat_pos) as lists of
# 0/1.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py wolf_goat_cabbage.json --check

# wolf_goat_cabbage: a FOX model for GroundFOX from DCP Rosetta.
#
# Farmer, wolf, goat and cabbage cross a river in a boat carrying the farmer and at most
# one item, never leaving the wolf with the goat or the goat with the cabbage unattended.
# Over the given number of stages (all on the starting shore at the first, all on the
# destination shore at the last, the boat flipping shore each stage) output each item's
# and the boat's shore (1 = destination, 0 = starting) at every stage.

_ITEMS = ["wolf_pos", "goat_pos", "cabbage_pos"]

_LINES = []
for _x in ["wolf_pos", "goat_pos", "cabbage_pos", "boat_pos"]:
    _LINES.append(f"! s [Stg(s)] : {_x}(s, 0) | {_x}(s, 1).")
    _LINES.append(f"! s [Stg(s)] : ~{_x}(s, 0) | ~{_x}(s, 1).")
for _x in ["wolf_pos", "goat_pos", "cabbage_pos", "boat_pos"]:
    _LINES.append(f"! s [Start(s)] : ~{_x}(s, 1).")
    _LINES.append(f"! s [Last(s)] : {_x}(s, 1).")
# Safety at every stage: a pair left together must be with the farmer.
for _v in (0, 1):
    _LINES.append(f"! s [Stg(s)] : ~wolf_pos(s, {_v}) | ~goat_pos(s, {_v}) | boat_pos(s, {_v}).")
    _LINES.append(f"! s [Stg(s)] : ~goat_pos(s, {_v}) | ~cabbage_pos(s, {_v}) | boat_pos(s, {_v}).")
# The boat flips shore at every stage.
_LINES.append("! s [Stg(s)] : ! t [Next(s, t)] : boat_pos(s, 0) | boat_pos(t, 0).")
_LINES.append("! s [Stg(s)] : ! t [Next(s, t)] : ~boat_pos(s, 0) | ~boat_pos(t, 0).")
# An item that changes shore must be on the boat's shore and cross with the farmer.
for _x in _ITEMS:
    _LINES.append(f"! s [Stg(s)] : ! t [Next(s, t)] : ~{_x}(s, 0) | ~{_x}(t, 1) | boat_pos(s, 0).")
    _LINES.append(f"! s [Stg(s)] : ! t [Next(s, t)] : ~{_x}(s, 1) | ~{_x}(t, 0) | boat_pos(s, 1).")
# At most one item crosses per stage.
for _i, _x in enumerate(_ITEMS):
    for _y in _ITEMS[_i + 1:]:
        for _a in (0, 1):
            for _b in (0, 1):
                _LINES.append(
                    f"! s [Stg(s)] : ! t [Next(s, t)] : ~{_x}(s, {_a}) | ~{_x}(t, {1 - _a}) "
                    f"| ~{_y}(s, {_b}) | ~{_y}(t, {1 - _b})."
                )

FOX = (
    "invocabulary { Stg/1 Start/1 Last/1 Next/2 }\n"
    "outvocabulary { wolf_pos/2 goat_pos/2 cabbage_pos/2 boat_pos/2 }\n"
    "theory {\n    " + "\n    ".join(_LINES) + "\n}\n"
)


def structure(instance):
    S = instance["stage"]
    return {
        "domain": range(max(S, 2)),
        "Stg": range(S),
        "Start": [0],
        "Last": [S - 1],
        "Next": [(s, s + 1) for s in range(S - 1)],
    }

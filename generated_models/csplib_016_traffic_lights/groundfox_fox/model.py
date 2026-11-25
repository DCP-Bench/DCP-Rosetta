# csplib_016_traffic_lights: a FOX model for GroundFOX from DCP Rosetta.
#
# Imagine a four-way traffic junction with eight traffic lights. Four lights (V1 to V4) are
# for vehicles, and four (P1 to P4) are for pedestrians. The lights have different states
# (e.g., red, green). The problem parameters list the combinations of light states (V_i, P_i,
# V_{i+1}, P_{i+1}) that are safe for intersecting roads, for i=1..4 (with V_5=V_1 and
# P_5=P_1); every other combination is disallowed to prevent accidents.
#
# Vehicle light states: 0=red, 1=red-yellow, 2=green, 3=yellow Pedestrian light states: 0=red,
# 1=green
#
# Print a valid 8-tuple of light states (lights) as a list of integers with the order [V1, V2,
# V3, V4, P1, P2, P3, P4].
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_016_traffic_lights.json --check

# csplib_016_traffic_lights: a FOX model for GroundFOX from DCP Rosetta.
#
# Four vehicle lights V1..V4 (0=red, 1=red-yellow, 2=green, 3=yellow) and four pedestrian lights
# P1..P4 (0=red, 1=green) at a four-way junction. For i=1..4 (with V5=V1, P5=P1) the quadruple
# (V_i, P_i, V_{i+1}, P_{i+1}) must be one of the safe combinations in the instance.
# Print the lights as [V1, V2, V3, V4, P1, P2, P3, P4].
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX_HEAD = """
invocabulary { Idx/1 Val/1 PVal/1 Allowed/4 }
outvocabulary { lights/2 }
theory {
"""


def _theory():
    lines = []
    for k in range(8):
        lines.append(f"    ? v [Val(v)] : lights({k}, v).")
        lines.append(f"    ! v [Val(v)] : ! w [Val(w) & ~(v = w)] : ~lights({k}, v) | ~lights({k}, w).")
    for k in range(4, 8):
        lines.append(f"    ! v [Val(v) & ~PVal(v)] : ~lights({k}, v).")
    for i in range(4):
        # Positions of (V_i, P_i, V_{i+1}, P_{i+1}) in the lights list.
        p = [i, 4 + i, (i + 1) % 4, 4 + (i + 1) % 4]
        lines.append(
            "    ! a [Val(a)] : ! b [Val(b)] : ! c [Val(c)] : ! d [Val(d) & ~Allowed(a,b,c,d)] : "
            f"~lights({p[0]}, a) | ~lights({p[1]}, b) | ~lights({p[2]}, c) | ~lights({p[3]}, d)."
        )
    return "\n".join(lines)


FOX = FOX_HEAD + _theory() + "\n}\n"


def structure(instance):
    allowed = [tuple(int(x) for x in row) for row in instance["allowed_tuples"]]
    return {
        "Idx": list(range(8)),
        "Val": [0, 1, 2, 3],
        "PVal": [0, 1],
        "Allowed": allowed,
    }

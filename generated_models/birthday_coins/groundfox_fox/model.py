# birthday_coins: a FOX model for GroundFOX from DCP Rosetta.
#
# Tommy was given 15 coins for his birthday (half-crowns, shillings and sixpence). When he
# added it up, he found that he had £1. 5s. 6d (one pound 5 shillings and 6 pences, see
# below). How many half-crowns was he given?
#
# (This puzzle involve coins from the old British currency. A pound is 20 shillings and a
# shilling is 12 pence (hence, a pound is 20 ⋅ 12 = 240 pence). A half-sovereign is 10
# shillings, a crown is 5 shillings, a double-florin is four shillings, a half-crown is 2
# shillings and sixpence (hence, a half-crown is 2 ⋅ 12 + 6 = 30 pence), a florin is 2
# shillings. £3. 2s. 6d. means three pounds, two shillings and six pence.).
#
# Print the number of half-crowns he was given (half_crowns).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py birthday_coins.json --check

# birthday_coins: a FOX model for GroundFOX from DCP Rosetta.
#
# Tommy was given 15 coins (half-crowns, shillings, sixpences) totalling 1 pound 5 shillings
# 6 pence. How many half-crowns was he given? Print the number of half-crowns (half_crowns).
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

# Money is counted in sixpences: a half-crown is 5 units, a shilling 2, a sixpence 1; the
# total is 306 pence = 51 units; the coin count is 15. Two layered chains of partial sums
# (units and coins) are walked backwards from the final state, one layer per coin kind.
FOX = """
invocabulary { Cnt/1 US/1 UBad/1 CS/1 CBad/1 Zero/1 UTarget/1 CTarget/1 Us0/3 Us1/3 Us2/3 Cs/3 }
outvocabulary { half_crowns/1 shilling/1 sixpence/1 UC/2 NC/2 }
theory {
    ? c [Cnt(c)] : half_crowns(c).
    ! c : ! d [Cnt(c) & Cnt(d) & c ~= d] : ~half_crowns(c) | ~half_crowns(d).
    ? c [Cnt(c)] : shilling(c).
    ! c : ! d [Cnt(c) & Cnt(d) & c ~= d] : ~shilling(c) | ~shilling(d).
    ? c [Cnt(c)] : sixpence(c).
    ! c : ! d [Cnt(c) & Cnt(d) & c ~= d] : ~sixpence(c) | ~sixpence(d).

    ! y [Zero(y)] : UC(0,y).
    ! y [US(y) & ~Zero(y)] : ~UC(0,y).
    ! y [Zero(y)] : NC(0,y).
    ! y [CS(y) & ~Zero(y)] : ~NC(0,y).

    ! y [UBad(y)] : ~UC(0,y).
    ! y [UBad(y)] : ~UC(1,y).
    ! y [UBad(y)] : ~UC(2,y).
    ! y [UBad(y)] : ~UC(3,y).
    ! y [CBad(y)] : ~NC(0,y).
    ! y [CBad(y)] : ~NC(1,y).
    ! y [CBad(y)] : ~NC(2,y).
    ! y [CBad(y)] : ~NC(3,y).

    ! y : ! c : ! x [Us0(y,c,x)] : ~UC(1,y) | ~half_crowns(c) | UC(0,x).
    ! y : ! c : ! x [Us1(y,c,x)] : ~UC(2,y) | ~shilling(c) | UC(1,x).
    ! y : ! c : ! x [Us2(y,c,x)] : ~UC(3,y) | ~sixpence(c) | UC(2,x).
    ! y : ! c : ! x [Cs(y,c,x)] : ~NC(1,y) | ~half_crowns(c) | NC(0,x).
    ! y : ! c : ! x [Cs(y,c,x)] : ~NC(2,y) | ~shilling(c) | NC(1,x).
    ! y : ! c : ! x [Cs(y,c,x)] : ~NC(3,y) | ~sixpence(c) | NC(2,x).

    ! y [US(y) & ~UTarget(y)] : ~UC(3,y).
    ? y [UTarget(y)] : UC(3,y).
    ! y [CS(y) & ~CTarget(y)] : ~NC(3,y).
    ? y [CTarget(y)] : NC(3,y).
}
"""


def structure(instance):
    cnt = list(range(16))          # coins of one kind: 0..15
    ubad, cbad = 52, 16            # sentinel states for "sum overflowed or went negative"
    us = list(range(52)) + [ubad]  # unit sums 0..51 (+ sentinel)
    cs = list(range(16)) + [cbad]  # coin counts 0..15 (+ sentinel)

    def table(weight, states, bad):
        rows = []
        for y in states:
            if y == bad:
                continue
            for c in cnt:
                x = y - weight * c
                rows.append((y, c, x if x >= 0 else bad))
        return rows

    return {
        "domain": list(range(0, 60)),
        "Cnt": cnt,
        "US": us,
        "UBad": [ubad],
        "CS": cs,
        "CBad": [cbad],
        "Zero": [0],
        "UTarget": [51],
        "CTarget": [15],
        "Us0": table(5, us, ubad),   # half-crown = 30d = 5 units
        "Us1": table(2, us, ubad),   # shilling = 12d = 2 units
        "Us2": table(1, us, ubad),   # sixpence = 6d = 1 unit
        "Cs": table(1, cs, cbad),
    }

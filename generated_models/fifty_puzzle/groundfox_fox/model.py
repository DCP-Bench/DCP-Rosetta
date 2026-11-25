# fifty_puzzle: a FOX model for GroundFOX from DCP Rosetta.
#
# A side show is described as follows: "There were a number of little dummies which you were
# to knock over with baseballs. The man said: 'Take as many throws as you like at a cent
# apiece and stand as close as you please. Add up the numbers on all the men that you knock
# down and when the sum amounts to exactly a given target sum, neither more nor less you get a
# genuine prize.'" The numbers on the dummies are given as a list of integers.
#
# Print the dummies that are knocked over (dummies) as a list of booleans.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py fifty_puzzle.json --check

"""fifty_puzzle: a FOX model for GroundFOX from DCP Rosetta.

dummies(i, b): dummy i is knocked over (b = 1) or not (b = 0). The chosen values must
sum to target_sum. FOX has no arithmetic, so the running sum is a chain of states
S(level, s) over shifted sums s = partial sum - lo, where lo is the sum of the negative
values (data). The chain is deterministic given dummies, so the final level may only
hold the target sum.
"""

FOX = """
invocabulary { Item/1 Level/1 First/1 Last/1 Next/2 Bool/1 Sm/1 Start/1 SNe/1 AddI/3 }
outvocabulary { dummies/2 S/2 }
theory {
    ! i [Item(i)] : ? b [Bool(b)] : dummies(i, b).
    ! i [Item(i)] : ! b [Bool(b)] : ! c [Bool(c) & b ~= c] : ~dummies(i, b) | ~dummies(i, c).
    ! l [First(l)] : ! s [Start(s)] : S(l, s).
    ! i [Item(i)] : ! j [Next(i, j)] : ! s [Sm(s)] : ~S(i, s) | dummies(i, 1) | S(j, s).
    ! i [Item(i)] : ! j [Next(i, j)] : ! s [Sm(s)] : ! r [AddI(i, s, r)] : ~S(i, s) | ~dummies(i, 1) | S(j, r).
    ! l [Last(l)] : ! s [SNe(s)] : ~S(l, s).
}
"""


def structure(instance):
    values = list(instance["values"])
    target = instance["target_sum"]
    n = len(values)
    lo = sum(v for v in values if v < 0)
    hi = sum(v for v in values if v > 0)
    off = -lo
    top = hi - lo
    sums = range(top + 1)
    return {
        "Item": range(n),
        "Level": range(n + 1),
        "First": [0],
        "Last": [n],
        "Next": [(i, i + 1) for i in range(n)],
        "Bool": [0, 1],
        "Sm": list(sums),
        "Start": [off],
        "SNe": [s for s in sums if s != target + off],
        "AddI": [(i, s, s + values[i]) for i in range(n) for s in sums if 0 <= s + values[i] <= top],
    }

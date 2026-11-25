# three_sum: a FOX model for GroundFOX from DCP Rosetta.
#
# Given a collection of integers, find exactly `m` elements that sum to zero.
#
# Print whether each element is selected (indices) as a list of booleans.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py three_sum.json --check

# three_sum: a FOX model for GroundFOX from DCP Rosetta.
#
# Select exactly m of the integers so that the selected ones sum to zero. Two one-hot chains
# run over the items: the count of selected items and the running sum (shifted so every
# partial sum is a non-negative element). indices[i] is true when item i is selected.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Item/1 Next/2 Lvl/1 Last/1 Cnt/1 Succ/2 Target/1 Sum/1 Zero/1 Add/3 }
outvocabulary { indices/2 ss/2 cc/2 }
theory {
    ! i [Item(i)] : indices(i,0) | indices(i,1).
    ! i [Item(i)] : ~indices(i,0) | ~indices(i,1).
    ! z [Zero(z)] : ss(0,z).
    ! u [u = 0] : cc(0,0).
    ! i [Lvl(i)] : ? s [Sum(s)] : ss(i,s).
    ! i [Lvl(i)] : ? c [Cnt(c)] : cc(i,c).
    ! i [Lvl(i)] : ! s [Sum(s)] : ! t [Sum(t) & s ~= t] : ~ss(i,s) | ~ss(i,t).
    ! i [Lvl(i)] : ! c [Cnt(c)] : ! d [Cnt(d) & c ~= d] : ~cc(i,c) | ~cc(i,d).
    ! i [Item(i)] : ! j [Next(i,j)] : ! s [Sum(s)] : ~ss(i,s) | indices(i,1) | ss(j,s).
    ! i [Item(i)] : ! j [Next(i,j)] : ! s [Sum(s)] : ! t [Sum(t) & Add(i,s,t)] : ~ss(i,s) | ~indices(i,1) | ss(j,t).
    ! i [Item(i)] : ! j [Next(i,j)] : ! c [Cnt(c)] : ~cc(i,c) | indices(i,1) | cc(j,c).
    ! i [Item(i)] : ! j [Next(i,j)] : ! c [Cnt(c)] : ! d [Succ(c,d)] : ~cc(i,c) | ~indices(i,1) | cc(j,d).
    ! l [Last(l)] : ! c [Cnt(c) & ~Target(c)] : ~cc(l,c).
    ! l [Last(l)] : ! s [Sum(s) & ~Zero(s)] : ~ss(l,s).
}
"""


def structure(instance):
    nums = instance["nums"]
    m = instance["m"]
    n = len(nums)
    lo = sum(x for x in nums if x < 0)
    hi = sum(x for x in nums if x > 0)
    size = hi - lo + 1
    # Sum element e stands for the partial sum e + lo; item i adds nums[i].
    add = [(i, e, e + nums[i]) for i in range(n) for e in range(size) if 0 <= e + nums[i] < size]
    return {
        "domain": list(range(max(size, n + 1, 2))),
        "Item": list(range(n)),
        "Next": [(i, i + 1) for i in range(n)],
        "Lvl": list(range(n + 1)),
        "Last": [n],
        "Cnt": list(range(n + 1)),
        "Succ": [(c, c + 1) for c in range(n)],
        "Target": [m] if 0 <= m <= n else [],
        "Sum": list(range(size)),
        "Zero": [-lo],
        "Add": add,
    }

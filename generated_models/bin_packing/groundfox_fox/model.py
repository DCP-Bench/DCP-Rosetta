# bin_packing: a FOX model for GroundFOX from DCP Rosetta.
#
# Given several items of specific weights and a number of bins of a fixed capacity, assign
# each item to a bin so that the total weight of the items in each bin does not exceed the
# capacity.
#
# Print the bin each item is assigned to (bins) as a list of numbers, 0-indexed.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py bin_packing.json --check

# bin_packing: a FOX model for GroundFOX from DCP Rosetta.
#
# Assign each item to one bin so that the total weight in each bin does not exceed the capacity.
# Output bins[i] is the 0-based bin of item i.
#
# The load of each bin is tracked layer by layer over the items (load(b, i, s): bin b holds
# load s before item i is placed), so the grounding grows with items x bins x capacity rather
# than with subsets of items.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Item/1 Bin/1 Load/1 Nxt/2 Add/3 Ovf/2 }
outvocabulary { bins/2 load/3 }
theory {
    ! i [Item(i)] : ? b [Bin(b)] : bins(i,b).
    ! i [Item(i)] : ! b [Bin(b)] : ! c [Bin(c) & b ~= c] : ~bins(i,b) | ~bins(i,c).
    ! b [Bin(b)] : load(b,0,0).
    ! i [Item(i)] : ! j [Nxt(i,j)] : ! b [Bin(b)] : ! s [Load(s)] : ! t [Add(i,s,t)] : ~bins(i,b) | ~load(b,i,s) | load(b,j,t).
    ! i [Item(i)] : ! j [Nxt(i,j)] : ! b [Bin(b)] : ! s [Load(s)] : ~load(b,i,s) | bins(i,b) | load(b,j,s).
    ! i [Item(i)] : ! s [Ovf(i,s)] : ! b [Bin(b)] : ~bins(i,b) | ~load(b,i,s).
}
"""


def structure(instance):
    weights = instance["weights"]
    capacity = instance["capacity"]
    num_bins = instance["num_bins"]
    n = len(weights)
    domain = max(n + 1, num_bins, capacity + 1, 1)
    return {
        "domain": list(range(domain)),
        "Item": list(range(n)),
        "Bin": list(range(num_bins)),
        "Load": list(range(capacity + 1)),
        "Nxt": [(i, i + 1) for i in range(n)],
        # Item i fits on top of load s: s + weights[i] stays within the capacity.
        "Add": [(i, s, s + weights[i]) for i in range(n)
                for s in range(capacity + 1) if s + weights[i] <= capacity],
        # Item i cannot be placed on top of load s at all.
        "Ovf": [(i, s) for i in range(n)
                for s in range(capacity + 1) if s + weights[i] > capacity],
    }

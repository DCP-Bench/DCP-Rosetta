# session2_subset_sum: a FOX model for GroundFOX from DCP Rosetta.
#
# A bank van had several bags of coins, each containing a number of coins from a given list
# (there are multiple bags of the same kind). While the van was parked on the street, thieves
# stole some bags. A total of a given number of coins were lost. It is required to find how
# many bags were stolen for each type of coin bag.
#
# Print the number of bags stolen for each type of coins (bags) as a list of integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session2_subset_sum.json --check

# session2_subset_sum: a FOX model for GroundFOX from DCP Rosetta.
#
# A bank van had several bags of coins, each containing a number of coins from a given list
# (there are multiple bags of the same kind). Some bags were stolen; a total number of coins was
# lost. Find how many bags were stolen for each type of coin bag (bags[i] for coin_numbers[i]).
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Stage/1 Typ/1 Nxt/2 Start/1 Last/1 Zero/1 Target/1 Reach/1 Succ/2 Cnt/2 Inc/4 Over/3 }
outvocabulary { bags/2 S/2 PS/2 PB/2 }
theory {
    // stage i holds the running total of the first i bag types: exactly one state per stage
    ! i [Start(i)] : ! z [Zero(z)] : S(i, z).
    ! i [Stage(i)] : ? s [Reach(s)] : S(i, s).
    ! i [Stage(i)] : ! s [Reach(s)] : ~S(i, s) | PS(i, s).
    ! i [Stage(i)] : ! s [Reach(s)] : ! t [Succ(s, t)] : ~PS(i, s) | PS(i, t).
    ! i [Stage(i)] : ! s [Reach(s)] : ! t [Succ(s, t)] : ~PS(i, s) | ~S(i, t).

    // exactly one count per bag type, within its range (a ladder for at most one)
    ! i [Typ(i)] : ? k [Cnt(i, k)] : bags(i, k).
    ! i [Typ(i)] : ! k [Reach(k) & ~Cnt(i, k)] : ~bags(i, k).
    ! i [Typ(i)] : ! k [Reach(k)] : ~bags(i, k) | PB(i, k).
    ! i [Typ(i)] : ! k [Reach(k)] : ! l [Succ(k, l)] : ~PB(i, k) | PB(i, l).
    ! i [Typ(i)] : ! k [Reach(k)] : ! l [Succ(k, l)] : ~PB(i, k) | ~bags(i, l).

    // adding bags of type i moves the running total from stage i to stage i+1
    ! i [Typ(i)] : ! j [Nxt(i, j)] : ! s [Reach(s)] : ! k [Cnt(i, k)] : ! t [Inc(i, s, k, t)] :
        ~S(i, s) | ~bags(i, k) | S(j, t).
    // a count that would exceed the total is impossible
    ! i [Typ(i)] : ! s [Reach(s)] : ! k [Over(i, s, k)] : ~S(i, s) | ~bags(i, k).

    // the final stage reaches the lost total
    ! i [Last(i)] : ! t [Target(t)] : S(i, t).
}
"""


def structure(instance):
    coins = instance["coin_numbers"]
    total = instance["total_coins_lost"]
    n = len(coins)
    values = range(total + 1)
    out = {
        "Stage": range(n + 1),
        "Typ": range(n),
        "Nxt": [(i, i + 1) for i in range(n)],
        "Start": [0],
        "Last": [n],
        "Zero": [0],
        "Target": [total],
        "Reach": values,
        "Succ": [(k, k + 1) for k in range(total)],
        "Cnt": [],
        "Inc": [],
        "Over": [],
    }
    for i, c in enumerate(coins):
        for k in range(total // c + 1):
            out["Cnt"].append((i, k))
            for s in values:
                t = s + c * k
                if t <= total:
                    out["Inc"].append((i, s, k, t))
                else:
                    out["Over"].append((i, s, k))
    return out

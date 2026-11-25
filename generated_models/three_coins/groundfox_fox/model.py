# three_coins: a FOX model for GroundFOX from DCP Rosetta.
#
# Three coins lie on a table in the order tails, heads, tails. In precisely three moves make
# them face either all heads or all tails. Each move consists of choosing one coin and
# flipping it over.
#
# Print the initial configuration followed by the configuration after each move (steps), to
# make all coins face either all heads or all tails, as a list of lists of booleans, where
# True means tails -1- and False means heads -0-.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py three_coins.json --check

# steps[i][j] is coin j after i moves (True = tails = 1). Each move flips exactly one
# coin: mv(k, j) marks the coin flipped between configurations k and k+1.
FOX = """
invocabulary { Step/1 Next/2 Last/1 Coin/1 Bool/1 InitVal/2 }
outvocabulary { steps/3 mv/2 }
theory {
    ! i [Step(i)] : ! j [Coin(j)] : steps(i, j, 0) | steps(i, j, 1).
    ! i [Step(i)] : ! j [Coin(j)] : ~steps(i, j, 0) | ~steps(i, j, 1).
    ! j [Coin(j)] : ! b [InitVal(j, b)] : steps(0, j, b).

    ! k [Step(k)] : ! l [Next(k, l)] : ? j [Coin(j)] : mv(k, j).
    ! k [Step(k)] : ! l [Next(k, l)] : ! j [Coin(j)] : ! i [Coin(i) & ~(i = j)] : ~mv(k, i) | ~mv(k, j).
    ! k [Step(k)] : ! l [Next(k, l)] : ! j [Coin(j)] : ! b [Bool(b)] : ~mv(k, j) | ~steps(k, j, b) | ~steps(l, j, b).
    ! k [Step(k)] : ! l [Next(k, l)] : ! j [Coin(j)] : ! b [Bool(b)] : mv(k, j) | ~steps(k, j, b) | steps(l, j, b).
    ! k [Step(k)] : ! l [Next(k, l)] : ! j [Coin(j)] : ! b [Bool(b)] : mv(k, j) | steps(k, j, b) | ~steps(l, j, b).

    ! i [Last(i)] : ! j [Coin(j)] : ! k [Coin(k) & ~(j = k)] : ! b [Bool(b)] : ! c [Bool(c) & ~(b = c)] : ~steps(i, j, b) | ~steps(i, k, c).
}
"""


def structure(instance):
    init = instance["init"]
    n = instance["num_moves"]
    return {
        "domain": list(range(max(n + 2, len(init) + 1))),
        "Step": list(range(n + 1)),
        "Next": [(k, k + 1) for k in range(n)],
        "Last": [n],
        "Coin": list(range(len(init))),
        "Bool": [0, 1],
        "InitVal": [(j, 1 if init[j] else 0) for j in range(len(init))],
    }

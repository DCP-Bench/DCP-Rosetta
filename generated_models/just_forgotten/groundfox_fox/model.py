# just_forgotten: a FOX model for GroundFOX from DCP Rosetta.
#
# Joe was furious when he forgot one of his bank account numbers. He remembered that it had
# all the digits from 0 to n-1 in some order, so he tried a number of sets without success.
#
# When Joe finally remembered his account number, he realised that in each set just a specific
# number of the digits were in their correct position and that, if one knew that, it was
# possible to work out his account number.
#
# Print Joe's account number (x) as a list of n integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py just_forgotten.json --check

# just_forgotten: a FOX model for GroundFOX from DCP Rosetta.
#
# Joe's account number x is a permutation of the digits 0..n-1. For each guessed set (a
# list of n digits), exactly num_correct_digits positions hold the same digit as x.
#
# For each guess s, a layered count cnt(s, i, j) says: among the first i positions, exactly j
# agree with the guess. Agreement at position i is x(i, d) for the guessed digit d = sets[s][i]
# (a data relation Dig). The count after all n positions is forced forward and must equal the
# target; the at-most-one constraint on the final layer makes the forced count the only one.

def _theory():
    return (
        "invocabulary { Pos/1 Digit/1 Set/1 Dig/3 Next/2 Inc/2 Layer/1 Last/1 Target/1 }\n"
        "outvocabulary { x/2 cnt/3 }\n"
        "theory {\n"
        "    ! i [Pos(i)] : ? d [Digit(d)] : x(i, d).\n"
        "    ! i [Pos(i)] : ! d [Digit(d)] : ! e [Digit(e) & d ~= e] : ~x(i, d) | ~x(i, e).\n"
        "    ! d [Digit(d)] : ! i [Pos(i)] : ! j [Pos(j) & i ~= j] : ~x(i, d) | ~x(j, d).\n"
        "    ! s [Set(s)] : cnt(s, 0, 0).\n"
        "    ! s [Set(s)] : ! i [Pos(i)] : ! d [Dig(s, i, d)] : ! i2 [Next(i, i2)] : "
        "! j [Layer(j)] : ! j2 [Inc(j, j2)] : ~cnt(s, i, j) | ~x(i, d) | cnt(s, i2, j2).\n"
        "    ! s [Set(s)] : ! i [Pos(i)] : ! d [Dig(s, i, d)] : ! i2 [Next(i, i2)] : "
        "! j [Layer(j)] : ~cnt(s, i, j) | x(i, d) | cnt(s, i2, j).\n"
        "    ! s [Set(s)] : ! l [Last(l)] : ! j [Target(j)] : cnt(s, l, j).\n"
        "    ! s [Set(s)] : ! l [Last(l)] : ! j [Layer(j)] : ! k [Layer(k) & j ~= k] : "
        "~cnt(s, l, j) | ~cnt(s, l, k).\n"
        "}\n"
    )


FOX = _theory()


def structure(instance):
    sets = instance["sets"]
    target = instance["num_correct_digits"]
    n = len(sets[0])
    return {
        "domain": range(0, n + 1),
        "Pos": range(n),
        "Digit": range(n),
        "Set": range(len(sets)),
        "Dig": [(s, i, sets[s][i]) for s in range(len(sets)) for i in range(n)],
        "Next": [(i, i + 1) for i in range(n)],
        "Inc": [(j, j + 1) for j in range(n)],
        "Layer": range(n + 1),
        "Last": [n],
        "Target": [target],
    }

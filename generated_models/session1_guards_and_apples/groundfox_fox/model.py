# session1_guards_and_apples: a FOX model for GroundFOX from DCP Rosetta.
#
# A boy wants to give an apple to a girl. To get to her, he has to pass through a number of
# gates, each with a guard. He bribes each guard with half of his apples, plus one. The boy
# does not have a knife, therefore he gives the guard an integer number of apples. After he’s
# given the apple to the girl, he has no apples left, so he has exactly one apple after the
# last gate.
#
# Print a list of numbers (apples), containing the number of apples before each gate, plus the
# number of apples after the last gate, so in total num_gates + 1 numbers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_guards_and_apples.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py session1_guards_and_apples.json --check

# session1_guards_and_apples: a FOX model for GroundFOX from DCP Rosetta.
#
# A boy passes num_gates gates. At each gate he gives the guard half of his apples plus one
# (an integer number of apples, so the count before each gate is even), and after the last
# gate he has exactly one apple left. Print the apples before each gate plus the count after
# the last gate (num_gates + 1 numbers, apples).
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

# Gate rule: before = 2 * after + 2. The chain is walked backwards from the final count of 1.
FOX = """
invocabulary { Pos/1 Dom/1 Nx/2 Half/2 Last/1 One/1 }
outvocabulary { apples/2 }
theory {
    ! i [Pos(i)] : ? a [Dom(a)] : apples(i,a).
    ! i [Pos(i)] : ! a [Dom(a)] : ! b [Dom(b) & a ~= b] : ~apples(i,a) | ~apples(i,b).
    ! i [Last(i)] : ? a [One(a)] : apples(i,a).
    ! i [Pos(i)] : ! j [Nx(i,j)] : ! b [Dom(b)] : ! a [Half(a,b)] : ~apples(j,b) | apples(i,a).
    ! i [Pos(i)] : ! j [Nx(i,j)] : ! b [Dom(b) & ~? a : Half(a,b)] : ~apples(j,b).
}
"""


def structure(instance):
    n = instance["num_gates"]
    # Counting back from 1 apple, the count before the k-th gate from the end is 3 * 2**k - 2,
    # so every value lies below 3 * 2**n; that bounds the domain of counts.
    bound = 3 * 2 ** n
    dom = list(range(bound))
    return {
        "domain": dom + [bound],
        "Pos": list(range(n + 1)),
        "Dom": dom,
        "Nx": [(i, i + 1) for i in range(n)],
        "Half": [(2 * b + 2, b) for b in dom if 2 * b + 2 < bound],
        "Last": [n],
        "One": [1],
    }

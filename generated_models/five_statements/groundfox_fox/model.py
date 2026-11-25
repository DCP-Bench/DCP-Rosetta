# five_statements: a FOX model for GroundFOX from DCP Rosetta.
#
# Determine which of the following statements is true.
#
# - Exactly one of these statements is false. - Exactly two of these statements are false. -
# Exactly three of these statements are false. - Exactly four of these statements are false. -
# Exactly five of these statements are false.
#
# Print whether each statement is true or false as 0/1 values (statements), in the order
# listed above.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py five_statements.json --check

# five_statements: a FOX model for GroundFOX from DCP Rosetta.
#
# Five statements: statement k (k = 1..5) says "exactly k of these statements are false".
# Find the truth value of each statement.
#
# Statements are indexed 0..4 (statement s says "exactly s+1 are false"). The false statements
# are counted by a layered relation cnt(i, j): among statements 0..i-1 exactly j are false.
# Layer i+1 follows layer i by statement i (a true statement keeps the count, a false one adds
# one). Each layer has exactly one count, so the last layer gives the total number of false
# statements, and statement s is true exactly when that total equals s+1.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Num/1 Stmt/1 Succ/2 Need/2 Zero/1 Last/1 }
outvocabulary { statements/2 cnt/2 }
theory {
    ! z [Zero(z)] : cnt(z, z).
    ! i [Num(i)] : ? j [Num(j)] : cnt(i, j).
    ! i [Num(i)] : ! j [Num(j)] : ! k [Num(k) & j ~= k] : ~cnt(i, j) | ~cnt(i, k).

    ! s [Stmt(s)] : statements(s, 0) | statements(s, 1).
    ! s [Stmt(s)] : ~statements(s, 0) | ~statements(s, 1).

    ! i [Stmt(i)] : ! i2 [Succ(i, i2)] : ! j [Num(j)] : ~cnt(i, j) | ~statements(i, 1) | cnt(i2, j).
    ! i [Stmt(i)] : ! i2 [Succ(i, i2)] : ! j [Num(j)] : ! j2 [Succ(j, j2)] : ~cnt(i, j) | statements(i, 1) | cnt(i2, j2).

    ! s [Stmt(s)] : ! j [Need(s, j)] : ! l [Last(l)] : ~cnt(l, j) | statements(s, 1).
    ! s [Stmt(s)] : ! j [Need(s, j)] : ! l [Last(l)] : ~statements(s, 1) | cnt(l, j).
}
"""


def structure(instance):
    return {
        "domain": range(6),
        "Num": range(6),
        "Stmt": range(5),
        "Succ": [(i, i + 1) for i in range(5)],
        "Need": [(s, s + 1) for s in range(5)],
        "Zero": [0],
        "Last": [5],
    }

# isbn: a FOX model for GroundFOX from DCP Rosetta.
#
# ISBN-13 Validation and Check Digit Calculation.
#
# Problem: An ISBN-13 (International Standard Book Number) is a 13-digit number where the last
# digit is a check digit calculated from the first 12 digits. The check digit is calculated as
# follows:
#
# 1. Multiply the first 12 digits alternately by 1 and 3 (starting with 1). 2. Sum the
# products. 3. The check digit is (10 - (sum % 10)) % 10.
#
# Given a list of 13 integers representing an ISBN-13, where -1 represents an unknown digit,
# find the values of the unknown digits such that the resulting number is a valid ISBN-13. An
# ISBN-13 must start with 978 or 979.
#
# Print the complete valid isbn (isbn) as a list of integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py isbn.json --check

FOX = """
invocabulary { Pos/1 Dig/1 Zero/1 One/1 Two/1 Last/1 Init/1 Prev/2 Fix/2 Step/4 }
outvocabulary { isbn/2 st/2 }
theory {
    ! i [Pos(i)] : ? d [Dig(d)] : isbn(i, d).
    ! i [Pos(i)] : ! d [Dig(d)] : ! e [Dig(e) & d ~= e] : ~isbn(i, d) | ~isbn(i, e).
    ! i [Pos(i)] : ! d [Fix(i, d)] : isbn(i, d).
    ! i [Zero(i)] : isbn(i, 9).
    ! i [One(i)] : isbn(i, 7).
    ! i [Two(i)] : isbn(i, 8) | isbn(i, 9).

    ! i [Pos(i)] : ? s [Dig(s)] : st(i, s).
    ! i [Pos(i)] : ! s [Dig(s)] : ! t [Dig(t) & s ~= t] : ~st(i, s) | ~st(i, t).
    ! i [Zero(i)] : ! s [Init(s)] : ! d [Dig(d)] : ! t [Step(i, s, d, t)] : ~isbn(i, d) | st(i, t).
    ! p [Pos(p)] : ! i [Prev(p, i)] : ! s [Dig(s)] : ! d [Dig(d)] : ! t [Step(i, s, d, t)] : ~st(p, s) | ~isbn(i, d) | st(i, t).
    ! i [Last(i)] : ! s [Init(s)] : st(i, s).
}
"""


def structure(instance):
    isbn = instance["isbn_init"]
    n = len(isbn)
    # Known digits of the instance (-1 marks an unknown digit).
    fix = [(i, d) for i, d in enumerate(isbn) if d >= 0]
    # Running check sum mod 10: weight 1 at even positions, 3 at odd positions.
    step = []
    for i in range(n):
        w = 1 if i % 2 == 0 else 3
        for s in range(10):
            for d in range(10):
                step.append((i, s, d, (s + w * d) % 10))
    return {
        "domain": list(range(max(n, 10) + 1)),
        "Pos": list(range(n)),
        "Dig": list(range(10)),
        "Zero": [0],
        "One": [1],
        "Two": [2],
        "Last": [n - 1],
        "Init": [0],
        "Prev": [(i - 1, i) for i in range(1, n)],
        "Fix": fix,
        "Step": step,
    }

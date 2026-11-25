# csplib_033_word_design: a FOX model for GroundFOX from DCP Rosetta.
#
# Find a set \( S \) of `num_words` strings (words) of length `n` over the alphabet \( W = \{
# A,C,G,T \} \) with the following properties:
#
# - Each word in \( S \) has 4 symbols from \{ C,G \}; - Each pair of distinct words in \( S
# \) differ in at least 4 positions; and - Each pair of words \( x \) and \( y \) in \( S \)
# (where \( x \) and \( y \) may be identical) are such that \( x^R \) and \( y^C \) differ in
# at least 4 positions. For example, when n=8, \( ( x_1,\ldots,x_8 )^R = ( x_8,\ldots,x_1 ) \)
# is the reverse of \( ( x_1,\ldots,x_8 ) \) and \( ( y_1,\ldots,y_8 )^C \) is the Watson-
# Crick complement of \( ( y_1,\ldots,y_8 ) \), i.e. the word where each \( A \) is replaced
# by a \( T \) and vice versa and each \( C \) is replaced by a \( G \) and vice versa.
#
# Print the set of words (words) as a list of lists of integers, where each integer represents
# a letter in the word: 1 for A, 2 for C, 3 for G, and 4 for T.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_033_word_design.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py csplib_033_word_design.json --check

# csplib_033_word_design: a FOX model for GroundFOX from DCP Rosetta.
#
# Find num_words words of length n over {A, C, G, T} (letters 1, 2, 3, 4) such that:
#  - each word has exactly 4 symbols from {C, G};
#  - distinct words differ in at least 4 positions;
#  - for every pair x, y (x = y allowed) the reverse of x and the Watson-Crick
#    complement of y differ in at least 4 positions. Complement: v -> 5 - v.
#
# Encoding: words(i, p, v) is the letter. "At least K positions differ" is a sequential
# counter per key (pair of words): T(key, p, c) means at least c differences among
# positions up to p; the difference indicators D only imply "differ", so the
# counter is sound. Position relations (Next, Mirror) and counts are data.

_INV = ("invocabulary { Word/1 Pos/1 Letter/1 ATL/1 CGL/1 Cnt/1 Ge2/1 Start/1 Last/1 "
        "Next/2 Prev/2 Mirror/2 Comp/2 PairLt/2 Need4/1 NeedAT/1 }")
_OUT = ("outvocabulary { words/3 DD/3 DX/3 TD/4 TX/4 CG/2 AI/2 TCG/3 TAI/3 }")

_LETTERS = ("! i [Word(i)] : ! p [Pos(p)] : ? v [Letter(v)] : words(i, p, v).\n"
            "! i [Word(i)] : ! p [Pos(p)] : ! v [Letter(v)] : ! u [Letter(u) & v ~= u] : ~words(i, p, v) | ~words(i, p, u).\n")

_INDICATORS = (
    # CG(i,p) implies the letter is not A/T; AI(i,p) implies it is not C/G.
    "! i [Word(i)] : ! p [Pos(p)] : ! v [ATL(v)] : ~CG(i, p) | ~words(i, p, v).\n"
    "! i [Word(i)] : ! p [Pos(p)] : ! v [CGL(v)] : ~AI(i, p) | ~words(i, p, v).\n"
    # DD(i,j,p) implies words i and j differ at p (i < j).
    "! i [Word(i)] : ! j [PairLt(i, j)] : ! p [Pos(p)] : ! v [Letter(v)] : ~DD(i, j, p) | ~words(i, p, v) | ~words(j, p, v).\n"
    # DX(i,j,p) implies reverse(x_i) and complement(x_j) differ at p.
    "! i [Word(i)] : ! j [Word(j)] : ! p [Pos(p)] : ! m [Mirror(p, m)] : ! u [Letter(u)] : ! v [Comp(u, v)] : "
    "~DX(i, j, p) | ~words(i, m, v) | ~words(j, p, u).\n"
)


def _counter(quant, key, tname, dname, need):
    """At least `need` positions with indicator dname, over the sequence Pos."""
    return (
        f"{quant} ! s [Start(s)] : ~{tname}({key}, s, 1) | {dname}({key}, s).\n"
        f"{quant} ! s [Start(s)] : ! c [Ge2(c)] : ~{tname}({key}, s, c).\n"
        f"{quant} ! p [Pos(p)] : ! q [Next(q, p)] : ! c [Cnt(c)] : "
        f"~{tname}({key}, p, c) | {tname}({key}, q, c) | {dname}({key}, p).\n"
        f"{quant} ! p [Pos(p)] : ! q [Next(q, p)] : ! c [Ge2(c)] : ! b [Prev(b, c)] : "
        f"~{tname}({key}, p, c) | {tname}({key}, q, c) | {tname}({key}, q, b).\n"
        f"{quant} ! l [Last(l)] : ! c [{need}(c)] : {tname}({key}, l, c).\n"
    )


_COUNTERS = (
    _counter("! i [Word(i)] :", "i", "TCG", "CG", "Need4")
    + _counter("! i [Word(i)] :", "i", "TAI", "AI", "NeedAT")
    + _counter("! i [Word(i)] : ! j [PairLt(i, j)] :", "i, j", "TD", "DD", "Need4")
    + _counter("! i [Word(i)] : ! j [Word(j)] :", "i, j", "TX", "DX", "Need4")
)


def _build_fox():
    body = _LETTERS + _INDICATORS + _COUNTERS
    th = "theory {\n" + "\n".join("    " + l for l in body.splitlines() if l.strip()) + "\n}\n"
    return _INV + "\n" + _OUT + "\n" + th


FOX = _build_fox()


def structure(instance):
    n = instance["n"]
    num_words = instance["num_words"]
    top = max(n + 1, num_words, 5)
    words = list(range(num_words))
    pos = list(range(n))
    cnt = list(range(n + 1))
    return {
        "domain": list(range(top)),
        "Word": words,
        "Pos": pos,
        "Letter": [1, 2, 3, 4],
        "ATL": [1, 4],
        "CGL": [2, 3],
        "Cnt": cnt,
        "Ge2": list(range(2, n + 1)),
        "Start": [0],
        "Last": [n - 1],
        "Next": [(p, p + 1) for p in range(n - 1)],
        "Prev": [(c - 1, c) for c in range(1, n + 1)],
        "Mirror": [(p, n - 1 - p) for p in range(n)],
        "Comp": [(1, 4), (4, 1), (2, 3), (3, 2)],
        "PairLt": [(i, j) for i in words for j in words if i < j],
        "Need4": [4],
        "NeedAT": [n - 4],
    }

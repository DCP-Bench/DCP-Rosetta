# de_bruijn_sequence: a FOX model for GroundFOX from DCP Rosetta.
#
# In combinatorial mathematics, a de Bruijn sequence of order n on a size-k alphabet A is a
# cyclic sequence in which every possible length-n string on A occurs exactly once as a
# substring. Such a sequence is denoted by B(k, n) and has length k^n.
#
# Print the de Bruijn sequence (de_bruijn) of a given order on a given size alphabet as a list
# of integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/de_bruijn_sequence.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py de_bruijn_sequence.json --check

FOX = """
invocabulary { Pos/1 Code/1 Dig/1 Lev/1 Top/1 Nxt/2 Ofs/3 Ext/3 }
outvocabulary { de_bruijn/2 C/3 }
theory {
    ! p [Pos(p)] : ? d [Dig(d)] : de_bruijn(p, d).
    ! p [Pos(p)] : ! d [Dig(d)] : ! e [Dig(e) & ~(d = e)] : ~de_bruijn(p, d) | ~de_bruijn(p, e).

    ! p [Pos(p)] : C(0, p, 0).
    ! l [Lev(l)] : ! p [Pos(p)] : ! c [Code(c)] : ! e [Code(e) & ~(c = e)] : ~C(l, p, c) | ~C(l, p, e).
    ! l [Lev(l)] : ! j [Nxt(l, j)] : ! p [Pos(p)] : ! q [Ofs(l, p, q)] : ! d [Dig(d)] : ! c [Code(c)] : ! e [Ext(c, d, e)] : ~C(l, p, c) | ~de_bruijn(q, d) | C(j, p, e).

    ! t [Top(t)] : ! c [Code(c)] : ! p [Pos(p)] : ! q [Pos(q) & ~(p = q)] : ~C(t, p, c) | ~C(t, q, c).
}
"""


def structure(instance):
    base = instance["base"]
    n = instance["n"]
    size = base ** n
    return {
        "Pos": list(range(size)),
        "Code": list(range(size)),
        "Dig": list(range(base)),
        "Lev": list(range(n + 1)),
        "Top": [n],
        "Nxt": [(l, l + 1) for l in range(n)],
        "Ofs": [(l, p, (p + l) % size) for l in range(n) for p in range(size)],
        "Ext": [(c, d, c * base + d) for c in range(size) for d in range(base) if c * base + d < size],
    }

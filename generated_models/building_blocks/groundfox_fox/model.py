# building_blocks: a FOX model for GroundFOX from DCP Rosetta.
#
# Each of a number of alphabet blocks has a single letter of the alphabet on each of its
# sides. In all, the blocks contain every letter but Q and Z. By arranging the blocks in
# various ways, you can spell all of the words in a given list, using each block for at most
# one letter of a word, so the letters of a word are all on different blocks. Each letter is
# on exactly one block, and each block has the same given number of sides. Can you figure out
# how the letters are arranged on the blocks?
#
# Print the solution as a list of num_letters numbers representing at which block each letter
# of the given alphabet is placed (dice), between 0 and num_blocks-1.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/building_blocks.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py building_blocks.json --check

FOX = """
invocabulary { Let/1 Blk/1 Lev/1 Cap/1 Nxt/2 Succ/2 Conf/2 }
outvocabulary { dice/2 S/3 }
theory {
    ! l [Let(l)] : ? b [Blk(b)] : dice(l, b).
    ! l [Let(l)] : ! b [Blk(b)] : ! c [Blk(c) & b ~= c] : ~dice(l, b) | ~dice(l, c).
    ! a [Let(a)] : ! b [Conf(a, b)] : ! c [Blk(c)] : ~dice(a, c) | ~dice(b, c).
    ! c [Blk(c)] : ! i [Let(i)] : ~dice(i, c) | S(c, i, 1).
    ! c [Blk(c)] : ! p [Let(p)] : ! i [Nxt(p, i)] : ! j [Lev(j)] : ~S(c, p, j) | S(c, i, j).
    ! c [Blk(c)] : ! p [Let(p)] : ! i [Nxt(p, i)] : ! q [Lev(q)] : ! j [Succ(q, j)] : ~dice(i, c) | ~S(c, p, q) | S(c, i, j).
    ! c [Blk(c)] : ! p [Let(p)] : ! i [Nxt(p, i)] : ! k [Cap(k)] : ~dice(i, c) | ~S(c, p, k).
}
"""


def structure(instance):
    alphabet = instance["alphabet"]
    L = instance["num_letters"]
    B = instance["num_blocks"]
    K = instance["num_sides"]
    index = {ch: i for i, ch in enumerate(alphabet)}
    # Letters that share a word must lie on different blocks.
    conf = set()
    for word in instance["words_str"]:
        letters = sorted({index[ch] for ch in word if ch in index})
        for a in letters:
            for b in letters:
                if a != b:
                    conf.add((a, b))
    # Each block carries at most num_sides letters: sequential-counter relations.
    N = max(L, B, K, 2)
    return {
        "domain": list(range(N + 1)),
        "Let": list(range(L)),
        "Blk": list(range(B)),
        "Lev": list(range(1, K + 1)),
        "Cap": [K],
        "Nxt": [(i, i + 1) for i in range(L - 1)],
        "Succ": [(q, q + 1) for q in range(1, K)],
        "Conf": sorted(conf),
    }

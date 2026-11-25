# set_game: a FOX model for GroundFOX from DCP Rosetta.
#
# Set (stylized as SET or SET!) is a real-time card game designed by Marsha Falco in 1974 and
# published by Set Enterprises in 1991. The deck consists of 81 unique cards that vary in four
# features across three possibilities for each kind of feature: number of shapes (one, two, or
# three), shape (diamond, squiggle, oval), shading (solid, striped, or open), and color (red,
# green, or purple). Each possible combination of features (e.g. a card with three striped
# green diamonds) appears as a card precisely once in the deck.
#
# In the game, certain combinations of three cards are said to make up a "set". For each one
# of the four categories of features—color, number, shape, and shading—the three cards must
# display that feature as either a) all the same, or b) all different. Put another way: For
# each feature the three cards must avoid having two cards showing one version of the feature
# and the remaining card showing a different version.
#
# For example, 3 solid red diamonds, 2 solid green squiggles, and 1 solid purple oval form a
# set, because the shadings of the three cards are all the same, while the numbers, the
# colors, and the shapes among the three cards are all different.
#
# For any set, the number of features that are constant (the same on all three cards) and the
# number of features that differ (different on all three cards) may break down as: all 4
# features differing; or 1 feature being constant and 3 differing; or 2 constant and 2
# differing; or 3 constant and 1 differing. (All 4 features being constant would imply that
# the three cards in the set are identical, which is impossible since no cards in the Set deck
# are identical.)
#
# Given a list of cards, each written as [number, shading, color, shape], find three different
# cards that form a set.
#
# Print the 0-based indices of the winning set of cards (winning_cards).
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py set_game.json --check

# set_game: a FOX model for GroundFOX from DCP Rosetta.

FOX = """
invocabulary { Card/1 Pos/1 Feat/1 Lt/2 Same/3 Diff/3 }
outvocabulary { winning_cards/2 }
theory {
    ! p [Pos(p)] : ? a [Card(a)] : winning_cards(p, a).
    ! p [Pos(p)] : ! a [Card(a)] : ! b [Card(b) & a ~= b] : ~winning_cards(p, a) | ~winning_cards(p, b).
    ! p [Pos(p)] : ! q [Pos(q) & Lt(p, q)] : ! a [Card(a)] : ~winning_cards(p, a) | ~winning_cards(q, a).
    ! f [Feat(f)] : ! b [Card(b)] : ! c [Card(c) & Same(f, b, c)] : ! a [Card(a) & Diff(f, a, b)] : ~winning_cards(0, a) | ~winning_cards(1, b) | ~winning_cards(2, c).
    ! f [Feat(f)] : ! a [Card(a)] : ! c [Card(c) & Same(f, a, c)] : ! b [Card(b) & Diff(f, a, b)] : ~winning_cards(0, a) | ~winning_cards(1, b) | ~winning_cards(2, c).
    ! f [Feat(f)] : ! a [Card(a)] : ! b [Card(b) & Same(f, a, b)] : ! c [Card(c) & Diff(f, a, c)] : ~winning_cards(0, a) | ~winning_cards(1, b) | ~winning_cards(2, c).
}
"""


def structure(instance):
    cards = instance["cards_data"]
    n = len(cards)
    # Per feature: which card pairs agree on that feature, which differ.
    same = [(f, a, b) for f in range(4) for a in range(n) for b in range(n)
            if cards[a][f] == cards[b][f]]
    diff = [(f, a, b) for f in range(4) for a in range(n) for b in range(n)
            if cards[a][f] != cards[b][f]]
    return {
        "Card": range(n),
        "Pos": range(3),
        "Feat": range(4),
        "Lt": [(0, 1), (0, 2), (1, 2)],
        "Same": same,
        "Diff": diff,
    }

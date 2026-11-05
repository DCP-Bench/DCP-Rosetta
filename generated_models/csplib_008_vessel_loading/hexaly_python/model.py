"""Vessel loading: place the containers on the deck without overlap, keeping certain classes apart."""
import hexaly.optimizer as hx


def build(instance):
    # deck_width = size of the deck across it; deck_length = size of the deck along it
    deck_width, deck_length = instance["deck_width"], instance["deck_length"]
    # width[i], length[i] = size of container i across and along the deck as given, before any turn;
    # classes[i] = class of container i, numbered from 1
    width, length, classes = instance["width"], instance["length"], instance["classes"]
    separation = instance["separation"]  # separation[a][b]: minimum distance between classes a + 1 and b + 1
    n = instance["n_containers"]  # number of containers to place
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Container i covers left[i]..right[i] across the deck and bottom[i]..top[i] along it, in a single
    # layer. It lies either as given (width across) or turned a quarter (length across):
    # turned[i] = 1 if container i is turned a quarter.
    turned = [model.bool() for _ in range(n)]
    # across[i], along[i] = extent of container i across and along the deck, given whether it is turned
    across = [model.iif(turned[i], length[i], width[i]) for i in range(n)]
    along = [model.iif(turned[i], width[i], length[i]) for i in range(n)]
    # left[i] = distance from the left edge of the deck to the left side of container i;
    # bottom[i] = distance from the bottom edge of the deck to the bottom side of container i.
    # Both start at 0 or more; the constraint below keeps the far sides on the deck.
    left = [model.int(0, deck_width) for _ in range(n)]
    bottom = [model.int(0, deck_length) for _ in range(n)]
    # right[i] and top[i] = the far sides of container i: its start plus its extent across or along
    right = [left[i] + across[i] for i in range(n)]
    top = [bottom[i] + along[i] for i in range(n)]
    # Every container lies on the deck
    for i in range(n):
        model.constraint(right[i] <= deck_width)
        model.constraint(top[i] <= deck_length)

    # Two containers do not overlap, and are at least their classes' separation apart along
    # or across the deck: one lies to the left of the other, or to its right, or below it, or above it,
    # with at least that separation between them
    for i in range(n):
        for j in range(i + 1, n):
            # minimum distance required between the classes of containers i and j (classes are numbered from 1)
            gap = separation[classes[i] - 1][classes[j] - 1]
            model.constraint(model.or_(right[i] + gap <= left[j], right[j] + gap <= left[i],
                                       top[i] + gap <= bottom[j], top[j] + gap <= bottom[i]))

    return optimizer, {"left": left, "right": right, "top": top, "bottom": bottom}

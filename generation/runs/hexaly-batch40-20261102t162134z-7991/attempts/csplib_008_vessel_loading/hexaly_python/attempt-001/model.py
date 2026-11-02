"""Vessel loading: place the containers on the deck without overlap, keeping certain classes apart."""
import hexaly.optimizer as hx


def build(instance):
    deck_width, deck_length = instance["deck_width"], instance["deck_length"]
    width, length, classes = instance["width"], instance["length"], instance["classes"]
    separation = instance["separation"]  # separation[a][b]: minimum distance between classes a + 1 and b + 1
    n = instance["n_containers"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Container i spans left..right across the deck and bottom..top along it, as placed
    # (width across, length along; not rotated)
    left = [model.int(0, deck_width - width[i]) for i in range(n)]
    bottom = [model.int(0, deck_length - length[i]) for i in range(n)]
    right = [left[i] + width[i] for i in range(n)]
    top = [bottom[i] + length[i] for i in range(n)]

    # Two containers do not overlap, and are at least their classes' separation apart along
    # or across the deck
    for i in range(n):
        for j in range(i + 1, n):
            gap = separation[classes[i] - 1][classes[j] - 1]
            model.constraint(model.or_(right[i] + gap <= left[j], right[j] + gap <= left[i],
                                       top[i] + gap <= bottom[j], top[j] + gap <= bottom[i]))

    return optimizer, {"left": left, "right": right, "top": top, "bottom": bottom}

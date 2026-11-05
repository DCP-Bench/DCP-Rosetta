"""Huey, Dewey and Louie: the cub scouts cannot lie, so all three statements are true; who is guilty?"""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    huey, dewey, louie = (model.bool() for _ in range(3))  # 1 if the boy is guilty

    # Huey: Dewey and Louie have an equal share in it; if one is guilty, so is the other
    model.constraint(dewey == louie)
    # Dewey: if Huey is guilty, then so am I
    model.constraint(huey <= dewey)
    # Louie: Dewey and I are not both guilty
    model.constraint(dewey + louie <= 1)

    return optimizer, {"huey": huey, "dewey": dewey, "louie": louie}

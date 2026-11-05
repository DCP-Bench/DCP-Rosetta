"""Contracting costs: the charge of each of six workmen, given what pairs of them are paid."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The painter's charge in dollars, the one number Hexaly has to find. Each pair total ties a man to the
    # next, so the other five charges follow one after the other: Hexaly searches one number far better than
    # six that must satisfy six equations exactly.
    painter = model.int(0, 5300)  # no charge exceeds the largest pair total
    paper_hanger = 1100 - painter        # paper hanger and painter are paid $1,100
    plumber = 1700 - painter             # painter and plumber are paid $1,700
    electrician = 1100 - plumber         # plumber and electrician are paid $1,100
    carpenter = 3300 - electrician       # electrician and carpenter are paid $3,300
    mason = 5300 - carpenter             # carpenter and mason are paid $5,300

    # The last pair, mason and painter, are paid $3,200
    model.constraint(mason + painter == 3200)
    # Nobody charges a negative amount
    for charge in (paper_hanger, plumber, electrician, carpenter, mason):
        model.constraint(charge >= 0)

    return optimizer, {"paper_hanger": paper_hanger, "painter": painter, "plumber": plumber,
                       "electrician": electrician, "carpenter": carpenter, "mason": mason}

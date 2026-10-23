"""
Model for birthday_coins problem.

Tommy was given 15 coins totaling £1 5s 6d.
Currency: 1 pound = 20 shillings, 1 shilling = 12 pence
Value in pence: £1 5s 6d = 240 + 60 + 6 = 306 pence

Coin values:
- half-crown = 2 shillings + 6 pence = 30 pence
- shilling = 12 pence
- sixpence = 6 pence

Find: number of half-crowns (half_crowns)
"""
from hermax.model import Model


def build(instance):
    m = Model()

    # Variables for each coin type
    # half_crowns: number of half-crown coins (30 pence each)
    # shillings: number of shilling coins (12 pence each)
    # sixpence: number of sixpence coins (6 pence each)
    half_crowns = m.int("half_crowns", 0, 15)
    shillings = m.int("shillings", 0, 15)
    sixpence = m.int("sixpence", 0, 15)

    # Constraint: total number of coins is 15
    m &= (half_crowns + shillings + sixpence == 15)

    # Constraint: total value is 306 pence (£1 5s 6d)
    # 30 pence per half-crown + 12 pence per shilling + 6 pence per sixpence
    m &= (30 * half_crowns + 12 * shillings + 6 * sixpence == 306)

    return m, {"half_crowns": half_crowns}

# csplib_001_car_sequencing: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Car sequencing: arrange the cars of a production run along an assembly line so
    that no option station is ever asked to handle more cars than it can cope with.
    Each car has one of several types, and a type fixes which options the car needs.
    Station o may handle at most at_most[o] of the cars that need option o in any
    per_slots[o] consecutive positions of the line. Build a sequence that contains
    exactly demand[t] cars of each type t and respects every station, and print the
    car type at each position of the line."""
    demand = instance["demand"]          # demand[t]: the number of cars of type t to build
    requires = instance["requires"]      # requires[t][o]: 1 when cars of type t need option o, else 0
    at_most = instance["at_most"]        # at_most[o]: the most cars needing option o allowed in one window
    per_slots = instance["per_slots"]    # per_slots[o]: the length of the window of consecutive positions for option o

    num_types = len(demand)
    num_options = len(at_most)
    # The line has one position per car. The statement gives no other length, so the
    # number of positions is the total demand.
    num_cars = sum(demand)

    model = gp.Model("car_sequencing")

    # car[p, t] is 1 when position p of the line holds a car of type t, and 0 when not
    car = model.addVars(num_cars, num_types, vtype=GRB.BINARY, name="car")

    # Every position of the line holds exactly one car, of exactly one type.
    model.addConstrs((car.sum(p, "*") == 1 for p in range(num_cars)), name="one_type_per_position")

    # Exactly demand[t] cars of each type t are built.
    model.addConstrs((car.sum("*", t) == demand[t] for t in range(num_types)), name="demand")

    # needs[p][o] is 1 when the car at position p requires option o, and 0 when not.
    # It is a linear expression over the car variables of that position.
    needs = [[gp.quicksum(car[p, t] for t in range(num_types) if requires[t][o] == 1)
              for o in range(num_options)]
             for p in range(num_cars)]

    # The statement does not say how windows at the ends of the line are treated, so only
    # windows lying wholly inside the line are constrained (no partial windows).
    # In every window of per_slots[o] consecutive positions, at most at_most[o] cars need option o.
    model.addConstrs((gp.quicksum(needs[p][o] for p in range(start, start + per_slots[o])) <= at_most[o]
                      for o in range(num_options)
                      for start in range(num_cars - per_slots[o] + 1)), name="station_capacity")

    # sequence[p] is the car type at position p of the line, an integer from 0 to num_types - 1.
    # It is tied to the car variables, so it is a single bounded integer per position.
    sequence = [model.addVar(lb=0, ub=num_types - 1, vtype=GRB.INTEGER, name=f"sequence[{p}]")
                for p in range(num_cars)]
    model.addConstrs((sequence[p] == gp.quicksum(t * car[p, t] for t in range(num_types))
                      for p in range(num_cars)), name="type_at_position")

    # There is no objective: any sequence that meets every requirement is a solution.

    return model, {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded

Blind model, after reading the lessons of 20261016-maxicp-java-models (ship amounts branched
value by value; the capacity shared between regions was not captured by any bound). Here every
unit of demand is a variable choosing its warehouse (units of a region listed in nondecreasing
order of the cost rank of their warehouse, so each shipment plan has one listing and cheap routes
are tried first), and MaxiCP's CostCardinalityMaxDC over these units, with the per-warehouse
capacity as the cardinality bound, gives the exact min-cost-flow lower bound on the shipping cost.
ships[w][j] are counts of the units. Opening Booleans are registered first. All five instances
prove the optimum: 0.4 s to 87 s in a local run (json:4, five regions, is the slow one).
Opening rules use the city names of warehouse_s to find New York, Los Angeles and Atlanta.

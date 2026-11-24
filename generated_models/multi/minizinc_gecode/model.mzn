% multi: a MiniZinc model from DCP Rosetta.
%
% This is a multi-commodity transportation problem. Given a set of origins, a set of destinations, and a
% set of products. Each origin i has a certain supply of each product p and each destination j has a
% certain demand for each product p. The cost of shipping one unit of product p from origin i to
% destination j is a given shipping cost. The problem aims to minimize the total cost of shipping all
% products from the origins to the destinations.
%
% Save this file as model.mzn. Download `multi.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py multi.json
%   minizinc model.mzn multi_1.json

array[int,int] of int: supply;           % supply[i,p]: units of product p that origin i can ship
array[int,int] of int: demand;           % demand[j,p]: units of product p that destination j needs
array[int,int] of int: limit;            % limit[i,j]: total units origin i can ship to destination j
array[int,int,int] of int: cost;         % cost[i,j,p]: cost of shipping one unit of p from i to j

set of int: Origins = index_set_1of2(supply);
set of int: Destinations = index_set_1of2(demand);
set of int: Products = index_set_2of2(supply);

int: ceiling = max(supply);              % no shipment is larger than the largest supply

% x[i,j,p]: units of product p shipped from origin i to destination j
array[Origins, Destinations, Products] of var 0..ceiling: x;

% the total cost of all shipments
var int: objective = sum(i in Origins, j in Destinations, p in Products)(cost[i,j,p] * x[i,j,p]);

% the products shipped from an origin do not exceed its supply of each product
constraint forall(i in Origins, p in Products)(sum(j in Destinations)(x[i,j,p]) <= supply[i,p]);

% each destination receives at least its demand of each product
constraint forall(j in Destinations, p in Products)(sum(i in Origins)(x[i,j,p]) >= demand[j,p]);

% the products shipped from an origin to a destination do not exceed the limit on that route
constraint forall(i in Origins, j in Destinations)(sum(p in Products)(x[i,j,p]) <= limit[i,j]);

solve minimize objective;

output ["{\"total_cost\": ", showJSON(objective), "}"];

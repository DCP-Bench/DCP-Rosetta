% facility_location: a MiniZinc model from DCP Rosetta.
%
% A company is considering opening warehouses in four cities to meet regional demands at minimal
% costs. The potential cities for these warehouses are New York, Los Angeles, Chicago, and Atlanta.
% Each open warehouse has a fixed weekly cost and can ship at most max_shipping units per week, and
% a closed one ships nothing. Shipping one unit from a warehouse to a region has a given cost, and
% each region must receive at least its weekly demand. The company needs to decide which warehouses
% to open, subject to these rules:
% 1. If the New York warehouse is opened, then the Los Angeles warehouse must also be opened.
% 2. No more than three warehouses can be operational in any given week.
% 3. Either the Atlanta or the Los Angeles warehouse must be opened.
% The objective is to minimize total costs: the fixed costs of the open warehouses plus the
% shipping costs.
%
% Save this file as model.mzn. Download `facility_location.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py facility_location.json
%   minizinc model.mzn facility_location_1.json

array[int] of string: warehouse_s;           % the city of each candidate warehouse
array[int] of int: fixed_costs;              % fixed weekly cost of each warehouse, if open
int: max_shipping;                           % most units an open warehouse ships per week
array[int] of int: demands;                  % weekly demand of each region
array[int, int] of int: shipping_costs;      % cost of shipping one unit from warehouse i to region j

set of int: Warehouses = index_set(warehouse_s);
set of int: Regions = index_set(demands);

int: new_york = min([i | i in Warehouses where warehouse_s[i] = "New York"]);
int: los_angeles = min([i | i in Warehouses where warehouse_s[i] = "Los Angeles"]);
int: atlanta = min([i | i in Warehouses where warehouse_s[i] = "Atlanta"]);

array[Warehouses] of var bool: open_warehouse;          % open_warehouse[i]: warehouse i is open
array[Warehouses, Regions] of var 0..max_shipping: ships; % ships[i, j]: units shipped from i to j

% a warehouse ships at most max_shipping units, and nothing when it is closed
constraint forall(i in Warehouses)
    (sum(j in Regions)(ships[i, j]) <= max_shipping * bool2int(open_warehouse[i]));
% each region receives at least its weekly demand
constraint forall(j in Regions)(sum(i in Warehouses)(ships[i, j]) >= demands[j]);
% if the New York warehouse is opened, the Los Angeles warehouse must also be opened
constraint open_warehouse[new_york] -> open_warehouse[los_angeles];
% no more than three warehouses are operational
constraint sum(i in Warehouses)(bool2int(open_warehouse[i])) <= 3;
% either the Atlanta or the Los Angeles warehouse must be opened
constraint open_warehouse[atlanta] \/ open_warehouse[los_angeles];

% total cost: the fixed costs of the open warehouses plus the shipping costs
var int: total_cost = sum(i in Warehouses)(fixed_costs[i] * bool2int(open_warehouse[i]))
    + sum(i in Warehouses, j in Regions)(shipping_costs[i, j] * ships[i, j]);
var int: objective = total_cost;

solve minimize objective;
output ["{\"total_cost\": ", show(total_cost),
        ", \"open_warehouse\": ", showJSON(open_warehouse),
        ", \"ships\": ", showJSON(ships), "}"];

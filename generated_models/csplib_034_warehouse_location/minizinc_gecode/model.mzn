% csplib_034_warehouse_location: a MiniZinc model from DCP Rosetta.
%
% In the Warehouse Location problem, a company must decide which warehouses to open from a set of candidate locations
% to supply a set of stores. Each warehouse has a fixed maintenance cost and a capacity limiting the number of stores it
% can supply. Each store must be supplied by exactly one open warehouse, and there is an associated supply cost that
% varies depending on the store and warehouse.
%
% The objective is to minimize the total cost, which is the sum of the maintenance costs for all opened warehouses and
% the supply costs for all stores.
%
% Save this file as model.mzn. Download `csplib_034_warehouse_location.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_034_warehouse_location.json
%   minizinc model.mzn csplib_034_warehouse_location_1.json

int: n_stores;                                    % the number of stores to supply
int: n_suppliers;                                 % the number of candidate warehouses
int: building_cost;                               % the maintenance cost of an open warehouse
set of int: Stores = 1..n_stores;                 % the stores
set of int: Warehouses = 1..n_suppliers;          % the candidate warehouses, numbered from 1
array[Warehouses] of int: capacity;               % capacity[w]: the most stores warehouse w can supply
array[Stores, Warehouses] of int: cost_matrix;    % cost_matrix[s,w]: the supply cost of store s from warehouse w

% open_warehouses[w]: warehouse w is open
array[Warehouses] of var bool: open_warehouses;
% assigned[s,w]: store s is supplied by warehouse w
array[Stores, Warehouses] of var bool: assigned;
% supplier_assignment[s]: the warehouse supplying store s, numbered from 0
array[Stores] of var 0..n_suppliers - 1: supplier_assignment;

var int: total_cost = building_cost * sum(w in Warehouses)(bool2int(open_warehouses[w]))
    + sum(s in Stores, w in Warehouses)(cost_matrix[s, w] * bool2int(assigned[s, w]));
var int: objective = total_cost;

% each store is supplied by exactly one warehouse
constraint forall(s in Stores)(sum(w in Warehouses)(bool2int(assigned[s, w])) = 1);

% a store is supplied only by an open warehouse
constraint forall(s in Stores, w in Warehouses)(assigned[s, w] -> open_warehouses[w]);

% each warehouse supplies no more stores than its capacity
constraint forall(w in Warehouses)(sum(s in Stores)(bool2int(assigned[s, w])) <= capacity[w]);

% the warehouse number of each store, numbered from 0
constraint forall(s in Stores)(supplier_assignment[s] = sum(w in Warehouses)(w * bool2int(assigned[s, w])) - 1);

solve minimize objective;

output ["{\"total_cost\": ", show(total_cost), ", \"open_warehouses\": ", showJSON(open_warehouses),
        ", \"supplier_assignment\": ", showJSON(supplier_assignment), "}"];

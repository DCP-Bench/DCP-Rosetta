% csplib_034_warehouse_location: a clingo model from DCP Rosetta.
%
% In the Warehouse Location problem, a company must decide which warehouses to open from a set of candidate locations to supply a set of stores. Each warehouse has a fixed maintenance cost and a capacity limiting the number of stores it can supply. Each store must be supplied by exactly one open warehouse, and there is an associated supply cost that varies depending on the store and warehouse. The objective is to minimize the total cost, which is the sum of the maintenance costs for all opened warehouses and the supply costs for all stores.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
% Save this file as model.lp. Download `csplib_034_warehouse_location.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_034_warehouse_location.json
%   python -m clingo model.lp csplib_034_warehouse_location_1.lp

% Input: n_suppliers(M): the number M of candidate warehouses (0..M-1); n_stores(N): the number N of stores
% (0..N-1); building_cost(B): the maintenance cost B of an open warehouse; capacity(W,C): the number C of
% stores warehouse W can supply; cost_matrix(S,W,C): the cost C of supplying store S from warehouse W.

warehouse(0..M-1) :- n_suppliers(M).
store(0..N-1) :- n_stores(N).

% open_warehouses(W,V): warehouse W is open (V = 1) or closed (V = 0)
{ open_warehouses(W,1) } :- warehouse(W).
open_warehouses(W,0) :- warehouse(W), not open_warehouses(W,1).

% supplier_assignment(S,W): store S is supplied by warehouse W; each store is supplied by exactly one warehouse
1 { supplier_assignment(S,W) : warehouse(W) } 1 :- store(S).

% a store is supplied only by an open warehouse
:- supplier_assignment(S,W), open_warehouses(W,0).

% a warehouse supplies no more stores than its capacity
:- capacity(W,C), #count { S : supplier_assignment(S,W) } > C.

% the total cost: the maintenance costs of the open warehouses plus the supply costs of the stores
total_cost(T) :- T = #sum { B,W : open_warehouses(W,1), building_cost(B) ;
                            C,S,W : supplier_assignment(S,W), cost_matrix(S,W,C) }.

% the total cost is as small as possible
#minimize { T : total_cost(T) }.

#show total_cost/1.
#show open_warehouses/2.
#show supplier_assignment/2.

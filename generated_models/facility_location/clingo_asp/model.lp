% facility_location: a clingo model from DCP Rosetta.
%
% A company is considering opening warehouses in four cities to meet regional demands at minimal costs. The potential cities for these warehouses are New York, Los Angeles, Chicago, and Atlanta. Each open warehouse has a fixed weekly cost and can ship at most max_shipping units per week, and a closed one ships nothing. Shipping one unit from a warehouse to a region has a given cost, and each region must receive at least its weekly demand. The company needs to decide which warehouses to open based on several constraints: 1. If the New York warehouse is opened, then the Los Angeles warehouse must also be opened. 2. No more than three warehouses can be operational in any given week. 3. Either the Atlanta or the Los Angeles warehouse must be opened. The objective is to determine the optimal set of warehouses to open and the distribution of shipments to various regions to minimize total costs: the fixed costs of the open warehouses plus the shipping costs.
%
% Save this file as model.lp. Download `facility_location.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py facility_location.json
%   python -m clingo model.lp facility_location_1.lp

% Input: warehouse_s(W, S) holds the name S of the city of warehouse W (indices 0-based); fixed_costs(W, F) holds the
% fixed weekly cost F of warehouse W; max_shipping(M) holds the most units M a warehouse ships per week; demands(R, D)
% holds the weekly demand D of region R; shipping_costs(W, R, C) holds the cost C of shipping one unit from W to R.

% the warehouses and the regions
warehouse(W) :- fixed_costs(W, _).
region(R) :- demands(R, _).

% each warehouse is open (open(W)) or not
{ open(W) : warehouse(W) }.

% each warehouse ships some number U of units to each region; more than the region's demand would only add cost
1 { ship(W, R, U) : U = 0..D } 1 :- warehouse(W), region(R), demands(R, D).

% a closed warehouse ships nothing
:- ship(W, R, U), U > 0, not open(W).

% an open warehouse ships at most max_shipping units per week in total
:- warehouse(W), max_shipping(M), #sum { U, R : ship(W, R, U) } > M.

% each region receives at least its weekly demand
:- region(R), demands(R, D), #sum { U, W : ship(W, R, U) } < D.

% constraint 1: if the New York warehouse is opened, then the Los Angeles warehouse must also be opened
:- open(W), warehouse_s(W, "New York"), warehouse_s(L, "Los Angeles"), not open(L).

% constraint 2: no more than three warehouses are operational
:- #count { W : open(W) } > 3.

% constraint 3: either the Atlanta or the Los Angeles warehouse must be opened (at least one of them)
:- warehouse_s(A, "Atlanta"), warehouse_s(L, "Los Angeles"), not open(A), not open(L).

% the largest cost of shipping one unit, and an upper bound on the total cost: all the fixed costs and
% the shipments of exactly the demand at the largest cost
maxcost(C) :- C = #max { X : shipping_costs(_, _, X) }.
bound(T) :- maxcost(C), T = #sum { F, f, W : fixed_costs(W, F); C*D, r, R : demands(R, D) }.

% the total cost, to be minimized: the fixed costs of the open warehouses plus the shipping costs
#minimize { F, f, W : open(W), fixed_costs(W, F); C*U, s, W, R : ship(W, R, U), shipping_costs(W, R, C) }.

% total_cost(Z) is that total cost. The bounded choice and check constraint below are an encoding chosen on
% purpose: writing total_cost as one #sum assignment over the choice atoms exhausts grounding (timeouts).
1 { total_cost(Z) : Z = 0..T } 1 :- bound(T).
:- total_cost(Z), Z != #sum { F, f, W : open(W), fixed_costs(W, F); C*U, s, W, R : ship(W, R, U), shipping_costs(W, R, C) }.

% the output: whether each warehouse is open, and the units shipped from each warehouse to each region
open_warehouse(W, true) :- open(W).
open_warehouse(W, false) :- warehouse(W), not open(W).
ships(W, R, U) :- ship(W, R, U).

#show total_cost/1.
#show open_warehouse/2.
#show ships/3.

% facility_location: a SWI-Prolog model from DCP Rosetta.
%
% A company is considering opening warehouses in four cities to meet regional demands at minimal costs. The potential
% cities for these warehouses are New York, Los Angeles, Chicago, and Atlanta. Each open warehouse has a fixed weekly
% cost and can ship at most max_shipping units per week, and a closed one ships nothing. Shipping one unit from a
% warehouse to a region has a given cost, and each region must receive at least its weekly demand.
%
% The company needs to decide which warehouses to open based on several constraints:
% 1. If the New York warehouse is opened, then the Los Angeles warehouse must also be opened.
% 2. No more than three warehouses can be operational in any given week.
% 3. Either the Atlanta or the Los Angeles warehouse must be opened.
%
% The objective is to determine the optimal set of warehouses to open and the distribution of shipments to various
% regions to minimize total costs: the fixed costs of the open warehouses plus the shipping costs.
%
% Save this file as model.pl. Download `facility_location.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('facility_location.json')" -t halt model.pl
%
% Data fields: warehouse_s (the name of each candidate warehouse city), fixed_costs (the weekly fixed cost of each
% warehouse), max_shipping (the most units an open warehouse ships per week), demands (the weekly demand of each
% region), shipping_costs (the cost of one unit from each warehouse, one row per warehouse, to each region); lists are
% indexed from 0.
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [total_cost-Total, open_warehouse-Open, ships-Ships], min(Total)) :-
    Names = Instance.warehouse_s,
    FixedCosts = Instance.fixed_costs,
    MaxShipping = Instance.max_shipping,
    Demands = Instance.demands,
    ShippingCosts = Instance.shipping_costs,
    length(Names, NW),                 % the number of candidate warehouses
    length(Demands, NR),               % the number of regions
    nth1(NewYork, Names, 'New York'),
    nth1(LosAngeles, Names, 'Los Angeles'),
    nth1(Atlanta, Names, 'Atlanta'),
    % Open[W] is 1 when warehouse W is open
    length(Open, NW),
    Open ins 0..1,
    % Ships[W][R] is the number of units warehouse W ships to region R
    length(Ships, NW),
    maplist({NR, MaxShipping}/[Row]>>(length(Row, NR), Row ins 0..MaxShipping), Ships),
    % a region never needs more than its demand from one warehouse
    maplist({Demands}/[Row]>>maplist([X, D]>>(X #=< D), Row, Demands), Ships),
    % a warehouse ships at most max_shipping units, and nothing when it is closed
    maplist({MaxShipping}/[Row, IsOpen]>>sum(Row, #=<, MaxShipping*IsOpen), Ships, Open),
    % every region receives its demand (shipping more than the demand only adds cost, so exactly the demand is
    % enough for an optimal plan)
    transpose(Ships, Regions),
    maplist([Column, Demand]>>sum(Column, #=, Demand), Regions, Demands),
    % rule 1: if New York is open, Los Angeles is open too
    nth1(NewYork, Open, OpenNewYork),
    nth1(LosAngeles, Open, OpenLosAngeles),
    OpenNewYork #=< OpenLosAngeles,
    % rule 2: no more than three warehouses are open
    sum(Open, #=<, 3),
    % rule 3: Atlanta or Los Angeles, or both, is open
    nth1(Atlanta, Open, OpenAtlanta),
    OpenAtlanta + OpenLosAngeles #>= 1,
    % the total cost is the fixed costs of the open warehouses plus the shipping cost of every unit shipped
    scalar_product(FixedCosts, Open, #=, FixedTotal),
    % the shipping cost of each region, which is at least its demand at the cheapest open warehouse's unit cost
    append(ShippingCosts, CostCells),
    append(Ships, ShipCells),
    max_list(CostCells, MaxCost),
    transpose(ShippingCosts, CostColumns),
    maplist(region_cost(Open, MaxCost), CostColumns, Regions, Demands, RegionCosts),
    sum(RegionCosts, #=, ShippingTotal),
    Total #= FixedTotal + ShippingTotal,
    append([Open, ShipCells, RegionCosts, [Total]], Vars).

% RegionCost is the cost of the units shipped into one region; each unit costs at least the cheapest open warehouse's
% unit cost to that region (a closed warehouse is priced at MaxCost, above every unit cost, so it is never the cheapest)
region_cost(Open, MaxCost, Costs, Column, Demand, RegionCost) :-
    scalar_product(Costs, Column, #=, RegionCost),
    maplist({MaxCost}/[C, IsOpen, V]>>(V #= C + MaxCost*(1 - IsOpen)), Costs, Open, Values),
    Values = [First|Rest],
    foldl([V, M0, M]>>(M #= min(M0, V)), Rest, First, Cheapest),
    RegionCost #>= Demand*Cheapest.

% The variables are labelled in the order of Vars: the open warehouses first, then the shipments. Domains are split in
% halves and the upper half is tried first.
labeling_options([leftmost, down, bisect]).

:- use_module(library(http/json)).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).

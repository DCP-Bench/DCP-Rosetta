% multi: a SWI-Prolog model from DCP Rosetta.
%
% This is a multi-commodity transportation problem. Given a set of origins, a set of destinations and a set of
% products, each origin has a certain supply of each product and each destination has a certain demand for each
% product. The cost of shipping one unit of a product from an origin to a destination depends on the origin, the
% destination and the product. Ship all the products from the origins to the destinations so that the total cost of
% shipping is as small as possible.
%
% Save this file as model.pl. Download `multi.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('multi.json')" -t halt model.pl
%
% Data fields: supply[I][P] (the supply of product P at origin I), demand[J][P] (the demand for product P at
% destination J), limit[I][J] (the most units that may be shipped from origin I to destination J, all products
% together), cost[I][J][P] (the cost of one unit of product P shipped from origin I to destination J). Lists are
% indexed from 0.
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).
:- use_module(library(http/json)).

model(Instance, Flat, [total_cost-TotalCost], min(TotalCost)) :-
    Supply = Instance.supply,
    Demand = Instance.demand,
    Limit = Instance.limit,
    Cost = Instance.cost,
    length(Supply, Origins),
    length(Demand, Destinations),
    Supply = [FirstSupply|_],
    length(FirstSupply, Products),
    append(Supply, SupplyFlat),
    max_list(SupplyFlat, MaxSupply),
    % Shipped[I][J][P] is the number of units of product P sent from origin I to destination J
    length(Shipped, Origins),
    maplist({Destinations, Products, MaxSupply}/[Row]>>
                (length(Row, Destinations),
                 maplist({Products, MaxSupply}/[Cell]>>
                             (length(Cell, Products), Cell ins 0..MaxSupply),
                         Row)),
            Shipped),
    append(Shipped, ShippedRows),
    append(ShippedRows, Flat),
    % an origin ships no more of each product than its supply of it
    maplist(within_supply, Shipped, Supply),
    % a destination receives at least its demand of each product
    transpose(Shipped, ByDestination),
    maplist(meets_demand, ByDestination, Demand),
    % no more than the limit is shipped from an origin to a destination, all products together
    maplist(within_limit, Shipped, Limit),
    % the total shipping cost
    maplist(shipping_cost, Shipped, Cost, RowCosts),
    sum(RowCosts, #=, TotalCost).

% within_supply(+ShippedFromOrigin, +Supply): per product, the amounts shipped from the origin add up to at most its supply
within_supply(Row, Available) :-
    transpose(Row, ByProduct),
    maplist([Amounts, Cap]>>sum(Amounts, #=<, Cap), ByProduct, Available).

% meets_demand(+ShippedToDestination, +Demand): per product, the amounts received add up to at least the demand
meets_demand(Column, Needed) :-
    transpose(Column, ByProduct),
    maplist([Amounts, Need]>>sum(Amounts, #>=, Need), ByProduct, Needed).

% within_limit(+ShippedFromOrigin, +Limits): the load on each origin-destination pair is within its limit
within_limit(Row, Caps) :-
    maplist([Cell, Cap]>>sum(Cell, #=<, Cap), Row, Caps).

% shipping_cost(+ShippedFromOrigin, +Prices, -Spent): the cost of the units shipped from one origin
shipping_cost(Row, Prices, Spent) :-
    maplist([Cell, Price, Part]>>scalar_product(Price, Cell, #=, Part), Row, Prices, Parts),
    sum(Parts, #=, Spent).

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

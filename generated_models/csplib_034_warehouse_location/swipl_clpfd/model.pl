% csplib_034_warehouse_location: a SWI-Prolog model from DCP Rosetta.
%
% A company decides which candidate warehouses to open, and assigns each store to exactly one open warehouse.
% Each warehouse has a fixed maintenance cost and can supply at most its capacity of stores, and each store has a
% supply cost that depends on the store and the warehouse. Minimise the total cost: the maintenance cost of the open
% warehouses plus the supply costs of all stores.
%
% Save this file as model.pl. Download `csplib_034_warehouse_location.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_034_warehouse_location.json')" -t halt model.pl
%
% Data fields: n_stores (the number of stores S), n_suppliers (the number of warehouses W), building_cost (the
% maintenance cost of each open warehouse), capacity (the number of stores each warehouse can supply, lists indexed
% from 0 by warehouse), cost_matrix (cost_matrix[S][W]: the supply cost of store S from warehouse W, indexed from 0).
:- use_module(library(clpfd)).

model(Instance, Vars, [total_cost-Total, open_warehouses-Open, supplier_assignment-Assign], min(Total)) :-
    S = Instance.n_stores, W = Instance.n_suppliers,
    Fixed = Instance.building_cost,
    Caps = Instance.capacity,
    Costs = Instance.cost_matrix,
    W1 is W - 1,
    numlist(0, W1, Indices),
    length(Open, W), Open ins 0..1,           % Open[W] is 1 when warehouse W is open
    % Supplies[I][W] is 1 when store I is supplied by warehouse W
    length(Supplies, S), maplist(length_is(W), Supplies),
    append(Supplies, SupplyFlat), SupplyFlat ins 0..1,
    % each store is supplied by exactly one warehouse, and only an open warehouse can supply
    maplist(one_warehouse, Supplies),
    maplist(only_if_open(Open), Supplies),
    % no warehouse supplies more stores than its capacity
    transpose(Supplies, Columns),
    maplist(within_capacity, Columns, Caps),
    % the warehouse of each store, from 0
    maplist(warehouse_of(Indices), Supplies, Assign),
    % the total cost: the maintenance cost of the open warehouses plus the supply costs
    sum(Open, #=, NOpen),
    Build #= Fixed*NOpen,
    append(Costs, CostFlat),
    scalar_product(CostFlat, SupplyFlat, #=, Supply),
    Total #= Build + Supply,
    append([SupplyFlat, Open, Assign, [NOpen, Build, Supply, Total]], Vars).

length_is(K, L) :- length(L, K).


labeling_options([ff, bisect]).

one_warehouse(Row) :- sum(Row, #=, 1).

only_if_open(Open, Row) :- maplist(#=<, Row, Open).

within_capacity(Column, Cap) :- sum(Column, #=<, Cap).

warehouse_of(Indices, Row, Warehouse) :- scalar_product(Indices, Row, #=, Warehouse).

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

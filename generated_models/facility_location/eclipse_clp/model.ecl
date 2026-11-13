% facility_location: an ECLiPSe model from DCP Rosetta.
%
% A company considers opening warehouses in four cities (New York, Los Angeles, Chicago and Atlanta) to meet the
% weekly demands of regions at minimal cost. An open warehouse has a fixed weekly cost and ships at most
% max_shipping units per week; a closed warehouse ships nothing. Shipping one unit from a warehouse to a region has
% a given cost, and each region must receive at least its weekly demand. Decide which warehouses to open and how
% many units each open warehouse ships to each region, so that the fixed costs of the open warehouses plus the
% shipping costs are minimal. The rules: if New York is opened, Los Angeles must also be opened; no more than
% three warehouses can be operational; either Atlanta or Los Angeles must be opened.
%
% Save this file as model.ecl. Download `facility_location.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py facility_location.json
%   eclipse -b model.ecl -e "run('facility_location_1.dat'), halt"

% Data fields: fixed_costs (the fixed weekly cost of each warehouse), demands (the weekly demand of each region),
% max_shipping (the most units an open warehouse ships), shipping_costs (the cost of one unit from warehouse i to
% region j, indexed [i][j]), warehouse_s (the names of the warehouses; the model does not read it and takes the warehouses in the order of the problem:
% New York, Los Angeles, Chicago, Atlanta).

:- lib(ic).
:- lib(lists).
:- lib(listut).

model(Instance, Vars, [open_warehouse-Open, ships-Ships, total_cost-Total], min(Total)) :-
    memberchk(fixed_costs-Fixed, Instance),
    memberchk(demands-Demands, Instance),
    memberchk(max_shipping-MaxShip, Instance),
    memberchk(shipping_costs-Costs, Instance),
    length(Fixed, NW),
    length(Demands, NR),
    % one 0/1 flag per warehouse, 1 when it is open
    length(Open, NW),
    Open :: 0..1,
    Open = [NY, LA, _Chicago, AT],
    % Ships[I][J]: the units shipped from warehouse I to region J
    length(Ships, NW),
    (   foreach(Row, Ships), param(NR, MaxShip) do
        length(Row, NR),
        Row :: 0..MaxShip
    ),
    % a closed warehouse ships nothing, and an open one ships at most max_shipping units
    (   foreach(Row, Ships), foreach(O, Open), param(MaxShip) do
        sum(Row) #=< MaxShip * O
    ),
    % each region receives at least its weekly demand
    (   for(J, 1, NR), param(Ships, Demands) do
        nth1(J, Demands, D),
        (   foreach(Row, Ships), foreach(X, Received), param(J) do
            nth1(J, Row, X)
        ),
        sum(Received) #>= D
    ),
    % if the New York warehouse is opened, the Los Angeles warehouse must also be opened
    NY #=< LA,
    % no more than three warehouses can be operational in any week
    sum(Open) #=< 3,
    % either the Atlanta or the Los Angeles warehouse must be opened
    AT + LA #>= 1,
    % the total cost: the fixed costs of the open warehouses plus the shipping costs
    FixedCost #= Fixed * Open,
    (   foreach(CRow, Costs), foreach(Row, Ships), foreach(RowCost, RowCosts) do
        RowCost #= CRow * Row
    ),
    ShippingCost #= sum(RowCosts),
    Total #= FixedCost + ShippingCost,
    append(Ships, FlatShips),
    append(Open, FlatShips, Vars).

% search: the warehouses first, then the shipments, lowest values first
search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_min, complete, []).

:- lib(branch_and_bound).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_module(gfd) -> Lib = gfd ; Lib = ic ),
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   Objective = max(Expr)
    ->  call(Lib:(Total #= Expr)), call(Lib:(Cost #= -Total)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   Objective = min(Expr)
    ->  call(Lib:(Cost #= Expr)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   run_search(Vars, Outputs)
    ),
    ( foreach(Name-Value, Outputs) do printf("%w = %w%n", [Name, Value]) ).

run_search(Vars, Outputs) :-
    (   current_predicate(search_goal/1) -> search_goal(Vars) ; labeling(Vars) ),
    term_variables(Outputs, Free),
    labeling(Free).

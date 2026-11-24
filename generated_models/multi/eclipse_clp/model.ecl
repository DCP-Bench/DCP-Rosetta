% multi: an ECLiPSe model from DCP Rosetta.
%
% This is a multi-commodity transportation problem. There is a set of origins, a set of destinations and a set of
% products. Each origin has a certain supply of each product, and each destination has a certain demand for each
% product. The cost of shipping one unit of a product from an origin to a destination is given. The problem is to
% minimize the total cost of shipping all products from the origins to the destinations, so that no origin ships more
% of a product than its supply, every destination receives at least its demand of each product, and the shipments on
% each origin-destination lane (all products together) stay within the limit of that lane.
%
% Save this file as model.ecl. Download `multi.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py multi.json
%   eclipse -b model.ecl -e "run('multi_1.dat'), halt"
%
% The data fields, lists indexed from 0 as in the JSON: supply[I][P] is the supply of product P at origin I;
% demand[J][P] is the demand of product P at destination J; limit[I][J] is the limit of the lane from origin I to
% destination J; cost[I][J][P] is the cost of shipping one unit of product P from origin I to destination J.

:- lib(ic).
:- lib(listut).
:- lib(branch_and_bound).

% Output total_cost: the total cost of the shipments.
model(Instance, Vars, [total_cost-Cost], min(Cost)) :-
    memberchk(supply-Supply, Instance),
    memberchk(demand-Demand, Instance),
    memberchk(limit-Limit, Instance),
    memberchk(cost-CostCube, Instance),
    length(Supply, NumOrigins),
    length(Demand, NumDestinations),
    Demand = [FirstDemand | _],
    length(FirstDemand, NumProducts),

    % Ship[I,J,P] is the amount of product P shipped from origin I to destination J (indexed from 1)
    dim(Ship, [NumOrigins, NumDestinations, NumProducts]),
    term_variables(Ship, Vars),            % the variables in the order I, J, P

    % each shipment lies between 0 and the limit of its lane, and the shipments of all products on a lane are
    % within the limit of the lane
    (   for(I, 1, NumOrigins), param(Ship, Limit, NumDestinations, NumProducts) do
        (   for(J, 1, NumDestinations), param(Ship, Limit, I, NumProducts) do
            nth1(I, Limit, LimitRow), nth1(J, LimitRow, L),
            (   for(P, 1, NumProducts), foreach(X, LaneVars), param(Ship, I, J) do
                subscript(Ship, [I, J, P], X)
            ),
            LaneVars :: 0..L,
            sum(LaneVars) #=< L
        )
    ),

    % each origin ships out no more of a product than its supply
    (   for(I, 1, NumOrigins), param(Ship, Supply, NumDestinations, NumProducts) do
        (   for(P, 1, NumProducts), param(Ship, Supply, I, NumDestinations) do
            (   for(J, 1, NumDestinations), foreach(X, Shipped), param(Ship, I, P) do
                subscript(Ship, [I, J, P], X)
            ),
            nth1(I, Supply, SupplyRow), nth1(P, SupplyRow, S),
            sum(Shipped) #=< S
        )
    ),

    % each destination receives at least its demand of each product
    (   for(J, 1, NumDestinations), param(Ship, Demand, NumOrigins, NumProducts) do
        (   for(P, 1, NumProducts), param(Ship, Demand, J, NumOrigins) do
            (   for(I, 1, NumOrigins), foreach(X, Received), param(Ship, J, P) do
                subscript(Ship, [I, J, P], X)
            ),
            nth1(J, Demand, DemandRow), nth1(P, DemandRow, D),
            sum(Received) #>= D
        )
    ),

    % the total cost of the shipments, which is to be as small as possible
    flatten(CostCube, CostFlat),
    Cost #= CostFlat * Vars.

% the search picks the variable with the fewest candidate values first and tries the lowest value first
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

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

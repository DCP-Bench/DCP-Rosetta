% aircraft_assignment: an ECLiPSe model from DCP Rosetta.
%
% Several types of aircraft are assigned to a set of routes so as to minimise the total operational cost. Each
% aircraft type has a limited number of available aircraft. Each route has a passenger demand that must be met.
% For each aircraft type and route the passenger capacity of one aircraft and its operational cost are given. Decide
% how many aircraft of each type to assign to each route so that all passenger demands are met, the availability
% of each aircraft type is not exceeded, and the overall cost is as small as possible. Allocation[I][J] is the
% number of aircraft of type I assigned to route J.
%
% Save this file as model.ecl. Download `aircraft_assignment.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py aircraft_assignment.json
%   eclipse -b model.ecl -e "run('aircraft_assignment_1.dat'), halt"

% Instance fields: availability (the number of aircraft of each type, a list indexed from 0 by type),
% capabilities (capabilities[I][J] is the passengers one aircraft of type I carries on route J, indexed from 0),
% costs (costs[I][J] is the operational cost of one aircraft of type I on route J, indexed from 0),
% demand (the passengers to carry on each route, a list indexed from 0 by route).
:- lib(ic).
:- lib(listut).

model(Instance, Vars, [allocation-Allocation], min(Total)) :-
    memberchk(availability-Availability, Instance),
    memberchk(capabilities-Capabilities, Instance),
    memberchk(costs-Costs, Instance),
    memberchk(demand-Demand, Instance),
    length(Availability, NumTypes),
    length(Demand, NumRoutes),
    % one row of the allocation per aircraft type, one column per route
    length(Allocation, NumTypes),
    ( foreach(Row, Allocation), param(NumRoutes) do length(Row, NumRoutes) ),
    concat_rows(Allocation, Vars),
    % the number of aircraft of each type on each route is a whole number, at least 0
    % and the aircraft of each type assigned in total do not exceed its availability
    ( foreach(Row, Allocation), foreach(Avail, Availability) do
        Row :: 0..Avail,
        sum(Row) #=< Avail
    ),
    % each route carries at least its passenger demand
    ( for(J, 0, NumRoutes-1), param(Allocation, Capabilities, Demand) do
        route_covered(J, Allocation, Capabilities, Demand)
    ),
    % the total operational cost of all the aircraft assigned, to be minimised
    concat_rows(Costs, FlatCosts),
    Total #= FlatCosts * Vars.

% route J carries at least its demand: the passengers carried by the aircraft of all types on that route
route_covered(J, Allocation, Capabilities, Demand) :-
    nth0(J, Demand, DemandJ),
    ( foreach(Row, Allocation), foreach(CapRow, Capabilities), foreach(Carried, CarriedList), param(J) do
        nth0(J, Row, X),
        nth0(J, CapRow, Cap),
        Carried #= Cap * X
    ),
    sum(CarriedList) #>= DemandJ.

% the rows of a list of rows, one after another
concat_rows([], []).
concat_rows([Row | Rows], Flat) :-
    concat_list(Row, Rest, Flat),
    concat_rows(Rows, Rest).

concat_list([], Ys, Ys).
concat_list([X | Xs], Ys, [X | Zs]) :- concat_list(Xs, Ys, Zs).

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

% aircraft_assignment: a SWI-Prolog model from DCP Rosetta.
%
% This problem involves assigning multiple types of aircraft to a set of routes to minimize the total operational
% cost. Each aircraft type has a limited number of available units. Each route has a specific passenger demand that
% must be satisfied. For each aircraft type and route, we are given the passenger capacity and the operational cost.
% The goal is to determine how many aircraft of each type to assign to each route to meet all passenger demands,
% stay within the availability limits for each aircraft type, and minimize the overall cost.
%
% Save this file as model.pl. Download `aircraft_assignment.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('aircraft_assignment.json')" -t halt model.pl
%
% Data fields: availability (the number of aircraft available of each type), capabilities (the passenger capacity
% of each type on each route, a list per type indexed from 0), costs (the operational cost of each type on each
% route, a list per type indexed from 0), demand (the passenger demand of each route, indexed from 0).
:- use_module(library(clpfd)).

% Rows[I][J] is the number of aircraft of type I assigned to route J
model(Instance, Vars, [allocation-Rows], min(Cost)) :-
    Availability = Instance.availability,
    Capabilities = Instance.capabilities,
    Costs = Instance.costs,
    Demand = Instance.demand,
    length(Availability, NTypes),
    length(Demand, NRoutes),
    length(Rows, NTypes),
    maplist(row_of_length(NRoutes), Rows),
    append(Rows, Vars),
    % no more aircraft of a type are assigned than are available
    maplist(within_availability, Availability, Rows),
    % each route gets passenger capacity at least equal to its demand
    transpose(Rows, Columns),
    transpose(Capabilities, CapabilityColumns),
    maplist(meets_demand, Columns, CapabilityColumns, Demand),
    % the total operational cost, to be minimised
    append(Costs, CostList),
    scalar_product(CostList, Vars, #=, Cost).

% a row with one count for each route
row_of_length(N, Row) :-
    length(Row, N).

% the counts of one type over the routes are non-negative and add up to no more than its availability
within_availability(Available, Row) :-
    Row ins 0..Available,
    sum(Row, #=<, Available).

% the passenger capacity of the aircraft on a route covers its demand
meets_demand(Counts, Capacities, Demand) :-
    scalar_product(Capacities, Counts, #>=, Demand).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
:- use_module(library(http/json)).
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

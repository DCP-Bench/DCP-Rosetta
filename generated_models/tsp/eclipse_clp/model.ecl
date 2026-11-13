% tsp: an ECLiPSe model from DCP Rosetta.
%
% The travelling salesman problem: given a list of cities and the distances between each pair of cities (or the
% locations of the cities), find the shortest possible route that visits each city exactly once and returns to the
% origin city. The distance between two locations is the Euclidean distance between the points, rounded to an integer.
%
% Save this file as model.ecl. Download `tsp.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py tsp.json
%   eclipse -b model.ecl -e "run('tsp_1.dat'), halt"

% Data fields: locations (the [X, Y] coordinates of each city, a list indexed from 0).
% Output travel_distance: the length of the shortest tour.
% Succ[I] is the city (numbered from 1) visited right after city I+1 on the tour.
:- lib(ic).

model(Instance, Succ, [travel_distance-Total], min(Total)) :-
    memberchk(locations-Locations, Instance),
    length(Locations, N),                  % the number of cities
    distance_matrix(Locations, Dist),      % Dist[I][J]: rounded distance from city I+1 to city J+1
    length(Succ, N),
    Succ :: 1..N,
    % the successors form a single tour through every city, returning to the origin city
    circuit(Succ),
    % the travel distance is the sum of the distances of the legs of the tour
    ( foreach(Row, Dist), foreach(S, Succ), foreach(Leg, Legs) do
        element(S, Row, Leg)
    ),
    sum(Legs) #= Total.

% The rounded Euclidean distance between every pair of cities.
distance_matrix(Locations, Dist) :-
    ( foreach(P, Locations), foreach(Row, Dist), param(Locations) do
        ( foreach(Q, Locations), foreach(D, Row), param(P) do
            rounded_distance(P, Q, D)
        )
    ).

rounded_distance([X1, Y1], [X2, Y2], D) :-
    D is integer(round(sqrt((X1 - X2) * (X1 - X2) + (Y1 - Y2) * (Y1 - Y2)))).

search_goal(Succ) :-
    search(Succ, 0, first_fail, indomain_min, complete, []).

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

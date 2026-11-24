% tsp: a SWI-Prolog model from DCP Rosetta.
%
% The travelling salesman problem: given a list of cities and the distances between each pair of cities (or the
% locations of the cities), what is the shortest possible route that visits each city exactly once and returns to
% the origin city? The distance between two points is their Euclidean distance rounded to an integer.
%
% Save this file as model.pl. Download `tsp.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/tsp.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('tsp.json')" -t halt model.pl
%
% Data fields: locations (the (x, y) point of each city, a list indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, Vars, [travel_distance-Total], min(Total)) :-
    Locations = Instance.locations,
    length(Locations, N),
    % the rounded Euclidean distance from every city to every city: Distances[From][To]
    maplist({Locations}/[From, Row]>>maplist(rounded_distance(From), Locations, Row),
            Locations, Distances),
    % Successor[C] is the city visited right after city C; cities are numbered 1..N here, as element/3 needs
    length(Successor, N),
    Successor ins 1..N,
    % the successors form one round trip that visits every city exactly once
    circuit(Successor),
    % the leg from each city to its successor, read from the city's row of distances
    length(Legs, N),
    maplist(leg_length, Distances, Successor, Legs),
    % the length of the round trip is the sum of its legs
    sum(Legs, #=, Total),
    % the decision variables and the auxiliary legs are labelled
    Vars = [Successor, Legs].

rounded_distance([X1, Y1], [X2, Y2], D) :-
    D is round(sqrt((X1 - X2) * (X1 - X2) + (Y1 - Y2) * (Y1 - Y2))).

leg_length(Row, City, Leg) :-
    element(City, Row, Leg).

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

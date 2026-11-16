% csplib_016_traffic_lights: a SWI-Prolog model from DCP Rosetta.
%
% A four-way traffic junction has eight traffic lights. Four lights (V1 to V4) are for vehicles and four (P1 to P4) are
% for pedestrians. Vehicle light states: 0 = red, 1 = red-yellow, 2 = green, 3 = yellow. Pedestrian light states:
% 0 = red, 1 = green. For i = 1 to 4 (with V5 = V1 and P5 = P1), the combination (V_i, P_i, V_(i+1), P_(i+1)) must be
% one of the safe combinations listed in the data; every other combination is disallowed to prevent accidents.
% Find a valid assignment of light states.
%
% Save this file as model.pl. Download `csplib_016_traffic_lights.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_016_traffic_lights.json')" -t halt model.pl
%
% Data fields: allowed_tuples (the safe combinations (V_i, P_i, V_(i+1), P_(i+1)), one per row).
:- use_module(library(clpfd)).

model(Instance, Vars, [lights-Lights]) :-
    Allowed = Instance.allowed_tuples,
    % Lights is [V1, V2, V3, V4, P1, P2, P3, P4]
    Lights = [V1, V2, V3, V4, P1, P2, P3, P4],
    Lights = Vars,
    % vehicle lights are 0..3, pedestrian lights are 0..1
    Vars = [V1, V2, V3, V4, P1, P2, P3, P4],
    [V1, V2, V3, V4] ins 0..3,
    [P1, P2, P3, P4] ins 0..1,
    % each pair of crossing roads, in turn (1,2), (2,3), (3,4), (4,1), is in a safe combination
    tuples_in([[V1, P1, V2, P2],
               [V2, P2, V3, P3],
               [V3, P3, V4, P4],
               [V4, P4, V1, P1]],
              Allowed).

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

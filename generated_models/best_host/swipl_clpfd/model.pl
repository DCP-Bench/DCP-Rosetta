% best_host: a SWI-Prolog model from DCP Rosetta.
%
% Six guests sit around a round dinner table. Some guests do not get along, so each guest must sit only next to the
% guests they get along with: Andrew only next to Dave and Frank; Betty only next to Cara and Erica; Cara only next to
% Betty and Frank; Dave only next to Andrew and Erica; Erica only next to Betty and Dave; Frank only next to Andrew and
% Cara. Find a seating order around the table in which every guest sits only next to the two guests they get along
% with.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).

model(_Instance, Seating, [x-Seating]) :-
    % guests numbered 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank; Next[G] lists the two guests G gets along with
    Next = [[3, 5], [2, 4], [1, 5], [0, 4], [1, 3], [0, 2]],
    findall([G, H], (nth0(G, Next, Hs), member(H, Hs)), Allowed),
    length(Seating, 6),
    Seating ins 0..5,
    all_distinct(Seating),                  % every guest has one seat
    Seating = [First|_],
    append(Seating, [First], Circle),       % the last seat is next to the first
    % every two guests in neighbouring seats get along
    adjacent_ok(Circle, Allowed).

% adjacent_ok(+Circle, +Allowed): each neighbouring pair of guests in Circle is an allowed pair.
adjacent_ok([_], _).
adjacent_ok([A, B|Rest], Allowed) :-
    tuples_in([[A, B]], Allowed),
    adjacent_ok([B|Rest], Allowed).

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

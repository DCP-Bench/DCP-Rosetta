% clock_triplets: a SWI-Prolog model from DCP Rosetta.
%
% Rearrange the numbers 1 to 12 on the face of a clock so that no three adjacent numbers have a sum higher than 21.
%
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).
:- use_module(library(lists)).

model(_Instance, Clock, [x-Clock]) :-
    N = 12,                                % the positions on the face
    length(Clock, N),
    Clock ins 1..N,                        % Clock[I] is the number at position I
    % each of the numbers 1 to 12 is placed once
    all_distinct(Clock),
    % going round the face, the first two positions follow the last, so every triplet of adjacent positions is checked
    Clock = [First, Second|_],
    append(Clock, [First, Second], Wrapped),
    triplets_at_most(Wrapped, 21).

% every three consecutive numbers of the list sum to at most Max
triplets_at_most([A, B, C|Rest], Max) :-
    !,
    A + B + C #=< Max,
    triplets_at_most([B, C|Rest], Max).
triplets_at_most(_, _).

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

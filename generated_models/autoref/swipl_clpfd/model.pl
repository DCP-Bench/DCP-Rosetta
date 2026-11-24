% autoref: a SWI-Prolog model from DCP Rosetta.
%
% Given an integer n > 0 and an integer m >= 0, find a non-empty finite series S = (s0, s1, ..., sn, sn+1) of
% integers between 0 and n such that (1) for each integer i from 0 to n there are exactly si occurrences of i in S,
% and (2) sn+1 = m.
%
% Save this file as model.pl. Download `autoref.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/autoref.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('autoref.json')" -t halt model.pl
%
% Data fields: n (the largest value in the series, so the series has n + 2 elements), m (the required last element).
:- use_module(library(clpfd)).

model(Instance, S, [s-S]) :-
    N = Instance.n,
    M = Instance.m,
    Length is N + 2,                        % the series S = (s0, ..., sn, sn+1)
    length(S, Length),
    S ins 0..N,                             % every element lies between 0 and n
    append(Counts, [M], S),                 % (s0, ..., sn) are the counts, and the last element is m
    % the value i occurs exactly si times in S, for each i from 0 to n
    numlist(0, N, Values),
    pairs_keys_values(Occurrences, Values, Counts),
    global_cardinality(S, Occurrences).

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

% csplib_007_all_interval: a SWI-Prolog model from DCP Rosetta.
%
% Given the n pitch-classes 0, 1, ..., n-1, find a series in which each pitch-class occurs exactly once and in which
% the musical intervals between neighbouring notes cover the full set of intervals from 1 to n-1. That is, a
% permutation s of 0 to n-1 whose interval vector v = (|s_2 - s_1|, |s_3 - s_2|, ..., |s_n - s_(n-1)|) is a
% permutation of 1 to n-1: an all-interval series of size n.
%
% Save this file as model.pl. Download `csplib_007_all_interval.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_007_all_interval.json')" -t halt model.pl
%
% Data fields: n (the number of pitch-classes, and the size of the series).
:- use_module(library(clpfd)).

model(Instance, Vars, [x-Xs, diffs-Ds]) :-
    N = Instance.n,
    Top is N - 1,
    % Xs[I] is the pitch-class of note I+1: each of 0 to n-1 occurs once
    length(Xs, N),
    Xs ins 0..Top,
    all_distinct(Xs),
    % Ds[I] is the interval between notes I+1 and I+2: the intervals are 1 to n-1, each once
    length(Ds, Top),
    Ds ins 1..Top,
    all_distinct(Ds),
    % each interval is the distance between two neighbouring notes
    intervals(Xs, Ds),
    Vars = [Xs, Ds].

intervals([_], []).
intervals([A, B|Rest], [D|Ds]) :-
    D #= abs(B - A),
    intervals([B|Rest], Ds).

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

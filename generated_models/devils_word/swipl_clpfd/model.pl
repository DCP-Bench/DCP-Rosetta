% devils_word: a SWI-Prolog model from DCP Rosetta.
%
% Given an array of integers, insert '+' or '-' operators before each integer in the array so that summing them up
% will result in a given total (666 for the devil's word).
%
% Save this file as model.pl. Download `devils_word.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('devils_word.json')" -t halt model.pl
%
% Data fields: arr (the integers, in order, indexed from 0), total (the sum the signed integers must reach).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, Result, [result-Result]) :-
    Arr = Instance.arr,
    Total = Instance.total,
    % Result[I] is Arr[I] with the sign chosen for it: either the number or its negative
    maplist([Value, Signed]>>(Negative is -Value, Signed in Negative \/ Value), Arr, Result),
    % the signed integers add up to the total
    sum(Result, #=, Total).

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

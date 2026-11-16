% session1_money_change: a SWI-Prolog model from DCP Rosetta.
%
% Alice has to give Bob some change. She has different types of coins of different values, and a certain number of
% coins of each value available. How can the change be composed from the available coins so that the number of coins
% used is as small as possible?
%
% Save this file as model.pl. Download `session1_money_change.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('session1_money_change.json')" -t halt model.pl
%
% Data fields: amount (the amount of change to give), types_of_coins (the value of each type of coin), available_coins
% (the number of coins of each type Alice has); lists indexed from 0.
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [coin_counts-Counts], min(Total)) :-
    Amount = Instance.amount,
    Values = Instance.types_of_coins,
    Available = Instance.available_coins,
    length(Values, NumTypes),
    length(Counts, NumTypes),              % Counts[I] is the number of coins of type I given to Bob
    Vars = [Total|Counts],
    % Alice can give no more coins of a type than she has
    max_list(Available, MaxHave),
    Counts ins 0..MaxHave,
    maplist([Count, Have]>>(Count #=< Have), Counts, Available),
    % the coins given add up to the amount of change
    scalar_product(Values, Counts, #=, Amount),
    % Total is the number of coins given, which is to be as small as possible
    sum(Counts, #=, Total).

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

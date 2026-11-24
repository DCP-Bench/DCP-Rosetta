% four_numbers: a SWI-Prolog model from DCP Rosetta.
%
% Given a list of up to four distinct integers between 1 and 10 (inclusive), find a list of three integers, also
% between 1 and 10 (inclusive), such that every one of the given numbers is the sum of a non-empty subset of the three.
% For example, for the numbers 1, 3, 7 and 8, the list 1, 2, 5 works: 1 = 1, 3 = 1 + 2, 7 = 2 + 5, 8 = 1 + 2 + 5.
% Give the list of three integers as x.
%
% Save this file as model.pl. Download `four_numbers.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/four_numbers.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('four_numbers.json')" -t halt model.pl
%
% Data fields: numbers (the list of the given numbers, indexed from 0).
:- use_module(library(clpfd)).

model(Instance, X, [x-X]) :-
    Numbers = Instance.numbers,
    length(X, 3),
    X ins 1..10,
    % each given number is the sum of some non-empty subset of the three
    maplist(covered(X), Numbers).

covered(X, N) :-
    Subsets = [[1], [2], [3], [1,2], [1,3], [2,3], [1,2,3]],
    maplist(subset_hits(X, N), Subsets, Hits),
    sum(Hits, #>=, 1).

% Hit is 1 when the subset of positions Positions sums to N
subset_hits(X, N, Positions, Hit) :-
    maplist(pick(X), Positions, Values),
    sum(Values, #=, Total),
    Hit #<==> (Total #= N).

pick(X, I, V) :-
    nth1(I, X, V).

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

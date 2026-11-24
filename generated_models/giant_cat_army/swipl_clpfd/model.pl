% giant_cat_army: a SWI-Prolog model from DCP Rosetta.
%
% Start with the list [0] and build it by repeatedly adding 5, adding 7, or taking the square root of the last
% number (only whole square roots count). All numbers in the list must be different whole numbers no larger than
% 60. The list must have 24 numbers, start with 0 and end with 14, and contain 2, 10 and 14 in that order, with
% other numbers allowed between them.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% Data fields: none, the problem has no data; the model reads nothing from the instance.
:- use_module(library(clpfd)).

model(_Instance, Vars, [x-X]) :-
    Length = 24,                           % the list has 24 numbers
    Max = 60,                              % every number is at most 60
    Goal = 14,                             % the list ends with 14
    length(X, Length),
    X ins 0..Max,
    % the list starts with 0 and ends with 14
    X = [0|_],
    last(X, Goal),
    % all the numbers are different
    all_distinct(X),
    % each number follows the previous one by adding 5, adding 7 or taking the square root
    steps(X),
    % 2 appears in the list, and 10 appears after it, and both come before the final 14
    element(I2, X, 2),                     % I2 is the position of 2 (counted from 1)
    element(I10, X, 10),                   % I10 is the position of 10 (counted from 1)
    I2 #< I10,
    I10 #< Length,
    Vars = [I2, I10|X].

% steps(+List): every element after the first is reached from the one before it by one of the three operations
steps([_]).
steps([A, B|Rest]) :-
    (B #= A + 5) #\/ (B #= A + 7) #\/ (A #= B * B),
    steps([B|Rest]).

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

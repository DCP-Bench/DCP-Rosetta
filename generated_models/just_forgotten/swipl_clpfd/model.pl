% just_forgotten: a SWI-Prolog model from DCP Rosetta.
%
% Joe forgot one of his bank account numbers. He remembered that it had all the digits from 0 to n-1 in some order,
% so he tried a number of sets, without success. In each set just a specific number of the digits are in their
% correct position, and that number is the same for every set. Knowing it is enough to work out the account number.
% Find the account number: a list of n digits, each of the digits from 0 to n-1 exactly once.
%
% Save this file as model.pl. Download `just_forgotten.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('just_forgotten.json')" -t halt model.pl
%
% Data fields: sets (the tried sets, indexed from 0, each a list of n digits), num_correct_digits (how many digits
% of each set are in their correct position in the account number).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(http/json)).

model(Instance, Vars, [x-X]) :-
    Sets = Instance.sets,
    Correct = Instance.num_correct_digits,
    Sets = [FirstSet|_],
    length(FirstSet, N),                   % the number of digits in the account number
    length(X, N),
    Last is N - 1,
    % the account number has all the digits from 0 to n-1, each exactly once
    X ins 0..Last,
    all_different(X),
    % each set has exactly Correct digits in their correct position
    maplist(same_position_count(X, Correct), Sets),
    Vars = X.

% same_position_count(+Digits, +Correct, +Set): exactly Correct positions hold the same digit in Set and in Digits
same_position_count(X, Correct, Set) :-
    pairwise_same(X, Set, Matches),
    sum(Matches, #=, Correct).

% pairwise_same(+Digits, +Set, -Flags): Flags[I] is 1 when position I holds the same digit in both lists, else 0
pairwise_same([], [], []).
pairwise_same([D|Ds], [S|Ss], [Flag|Flags]) :-
    Flag #<==> (D #= S),
    pairwise_same(Ds, Ss, Flags).

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

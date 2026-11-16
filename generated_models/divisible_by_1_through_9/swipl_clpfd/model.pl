% divisible_by_1_through_9: a SWI-Prolog model from DCP Rosetta.
%
% Find a 10 digit number that uses each of the digits 0 to 9 exactly once and where the number formed by the first n
% digits of the number is divisible by n. The digits are read from left to right: in the number abcd, the number a
% is divisible by 1, the number ab by 2, the number abc by 3 and the entire number abcd by 4.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
:- use_module(library(clpfd)).
:- use_module(library(apply)).

model(_Instance, [Digits, Prefixes], [digits-Digits]) :-
    length(Digits, 10),
    Digits ins 0..9,
    all_distinct(Digits),              % each digit is used exactly once
    Digits = [First|_],
    First #\= 0,                       % a 10 digit number does not start with zero
    % Prefixes[N-1] is the number formed by the first N digits
    prefixes(Digits, 0, Prefixes),
    numlist(1, 10, Ns),
    % the number formed by the first N digits is divisible by N
    maplist(divisible_by, Prefixes, Ns).

% Prefixes of the digit list: each one is the previous prefix shifted one place left, plus the next digit.
prefixes([], _, []).
prefixes([D|Ds], Before, [P|Ps]) :-
    P #= 10*Before + D,
    prefixes(Ds, P, Ps).

divisible_by(Prefix, N) :- Prefix mod N #= 0.

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

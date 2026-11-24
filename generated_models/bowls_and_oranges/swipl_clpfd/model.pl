% bowls_and_oranges: a SWI-Prolog model from DCP Rosetta.
%
% Bowls numbered from 1 are placed in a line at intervals of 1 metre. All the oranges are placed in the bowls, with no
% more than one orange in each bowl, so that there are no three oranges A, B and C such that the distance between A and
% B is equal to the distance between B and C. Give the bowls holding the oranges, in ascending order.
%
% Save this file as model.pl. Download `bowls_and_oranges.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('bowls_and_oranges.json')" -t halt model.pl
%
% Data fields: n (the number of bowls), m (the number of oranges).
:- use_module(library(clpfd)).

model(Instance, X, [x-X]) :-
    N = Instance.n,
    M = Instance.m,
    length(X, M),                           % X[I]: the bowl holding the I-th orange, counted from 0
    X ins 1..N,
    chain(X, #<),                           % the oranges sit in ascending bowls, one orange to a bowl
    % no three oranges I < J < K (in bowl order) are equally spaced: the gap from I to J differs from the gap from J to K
    findall(I-J-K, (between(1, M, I), J0 is I + 1, between(J0, M, J), K0 is J + 1, between(K0, M, K)), Triples),
    maplist(not_evenly_spaced(X), Triples).

% The oranges I, J, K (positions in X, counted from 1) are not evenly spaced.
not_evenly_spaced(X, I-J-K) :-
    nth1(I, X, A),
    nth1(J, X, B),
    nth1(K, X, C),
    B - A #\= C - B.

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

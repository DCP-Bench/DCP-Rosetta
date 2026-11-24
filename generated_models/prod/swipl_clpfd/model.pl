% prod: a SWI-Prolog model from DCP Rosetta.
%
% Consider a problem where we have a set P. For each element j in P, we have a parameter a[j], a parameter c[j], and a
% parameter u[j]. We also have a global parameter b. We have a variable X[j] for each j in P. The goal is to maximize
% the total profit, which is the sum of c[j] * X[j] for all j in P. The constraints are that the sum of (1/a[j]) * X[j]
% for all j in P should be less than or equal to b, and X[j] should be between 0 and u[j] for all j in P.
%
% Save this file as model.pl. Download `prod.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('prod.json')" -t halt model.pl
%
% Data fields: a (the value a[j] of each element j), b (the global parameter b), c (the profit c[j] of each element j),
% u (the upper bound u[j] of each element j), lists indexed from 0.
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(http/json)).

model(Instance, Xs, [x-Xs, total_profit-Profit], max(Profit)) :-
    A = Instance.a,
    B = Instance.b,
    C = Instance.c,
    U = Instance.u,
    length(A, N),
    length(Xs, N),
    % X[j] is an integer from 0 up to u[j]
    maplist(upper_bound, Xs, U),
    % 1/a[j] is not a whole number, so the resource constraint is multiplied through by P, the product of all a[j]
    foldl(times, A, 1, P),
    maplist(scaled(P), A, Scales),          % Scales[j] = P / a[j], a whole number since a[j] divides P
    Limit is B * P,
    % the sum of (1/a[j]) * X[j] is at most b, so the sum of (P/a[j]) * X[j] is at most b * P
    scalar_product(Scales, Xs, #=<, Limit),
    % the total profit is the sum of c[j] * X[j]
    scalar_product(C, Xs, #=, Profit).

% upper_bound(-X, +U): X is an integer from 0 up to U
upper_bound(X, U) :- X in 0..U.

% times(+X, +P0, -P): P is P0 times X, for foldl/4
times(X, P0, P) :- P is P0 * X.

% scaled(+P, +A, -S): S is P divided by A
scaled(P, A, S) :- S is P // A.

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

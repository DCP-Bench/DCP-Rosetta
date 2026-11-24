% csplib_044_steiner: a SWI-Prolog model from DCP Rosetta.
%
% The ternary Steiner problem of order n: find n(n-1)/6 triples of distinct elements from 1 to n such that any two
% triples have at most one element in common. (It is solvable when n mod 6 is 1 or 3.)
%
% Save this file as model.pl. Download `csplib_044_steiner.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_044_steiner.json')" -t halt model.pl
%
% Data fields: n (the order of the Steiner system: the number of elements, with column J holding element J+1).
:- use_module(library(clpfd)).

model(Instance, Vars, [sets-Rows]) :-
    N = Instance.n,
    T is N*(N-1)//6,                          % the number of triples
    length(Rows, T), maplist(length_is(N), Rows),   % Rows[I][J] = 1 when triple I holds element J+1
    append(Rows, Cells), Cells ins 0..1,
    % each triple holds exactly three elements
    maplist(sum_is(3), Rows),
    % any two triples have at most one element in common
    at_most_one_shared(Rows),
    % redundant: any two elements lie together in exactly one triple
    transpose(Rows, Cols),
    pairs_meet_once(Cols),
    Vars = Cells.

length_is(K, L) :- length(L, K).

sum_is(S, Row) :- sum(Row, #=, S).

at_most_one_shared([]).
at_most_one_shared([Row|Rows]) :-
    maplist(shares_at_most_one(Row), Rows),
    at_most_one_shared(Rows).

shares_at_most_one(Row, Other) :-
    maplist(both, Row, Other, Products),
    sum(Products, #=<, 1).

pairs_meet_once([]).
pairs_meet_once([Col|Cols]) :-
    maplist(meet_once(Col), Cols),
    pairs_meet_once(Cols).

meet_once(Col, Other) :-
    maplist(both, Col, Other, Products),
    sum(Products, #=, 1).

both(A, B, P) :- P #= A*B.

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

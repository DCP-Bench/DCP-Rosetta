% csplib_028_bibd: a SWI-Prolog model from DCP Rosetta.
%
% Balanced incomplete block design: arrange v objects into b blocks so that each block contains exactly k objects,
% each object occurs in exactly r blocks, and every two distinct objects occur together in exactly lambda blocks.
% Equivalently, find a v by b matrix of 0s and 1s with exactly r ones in each row, k ones in each column, and a
% scalar product of lambda between any two distinct rows.
%
% Save this file as model.pl. Download `csplib_028_bibd.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_028_bibd.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_028_bibd.json')" -t halt model.pl
%
% Data fields: v (the number of objects, the rows), b (the number of blocks, the columns), r (the number of blocks
% each object occurs in), k (the number of objects in each block), l (the lambda: the number of blocks two distinct
% objects share).
:- use_module(library(clpfd)).

model(Instance, Vars, [matrix-Rows]) :-
    V = Instance.v, B = Instance.b, R = Instance.r, K = Instance.k, L = Instance.l,
    length(Rows, V), maplist(length_is(B), Rows),   % Rows[I][J] = 1 when object I is in block J
    append(Rows, Cells), Cells ins 0..1,
    % each object occurs in exactly r blocks
    maplist(sum_is(R), Rows),
    % each block contains exactly k objects
    transpose(Rows, Cols),
    maplist(sum_is(K), Cols),
    % every two distinct objects occur together in exactly lambda blocks
    pairs_share(L, Rows),
    Vars = Cells.

length_is(K, L) :- length(L, K).

sum_is(S, Row) :- sum(Row, #=, S).

pairs_share(_, []).
pairs_share(L, [Row|Rows]) :-
    maplist(shares(L, Row), Rows),
    pairs_share(L, Rows).

shares(L, Row, Other) :-
    maplist(both, Row, Other, Products),
    sum(Products, #=, L).

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

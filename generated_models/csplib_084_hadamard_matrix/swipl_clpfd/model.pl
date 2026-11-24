% csplib_084_hadamard_matrix: a SWI-Prolog model from DCP Rosetta.
%
% For every odd positive integer l (and m = (l - 1) / 2), the Legendre pairs problem asks for two sequences
% a1, ..., al and b1, ..., bl, each value either -1 or +1, such that
% - for every shift s = 1, ..., m: PAF(A, s) + PAF(B, s) = -2, where PAF is the periodic autocorrelation function
%   PAF(A, s) = sum over i = 1, ..., l of ai * a(i+s), with i+s taken mod l when it exceeds l;
%   and PAF(B, s) is defined in the same way for B;
% - the values of A sum to 1, and the values of B sum to 1.
%
% Save this file as model.pl. Download `csplib_084_hadamard_matrix.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_084_hadamard_matrix.json')" -t halt model.pl
%
% Data fields: l (the odd length of each sequence).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, Vars, [a-As, b-Bs]) :-
    L = Instance.l,
    Shifts is (L - 1) // 2,
    % As[I] and Bs[I] are the values of a(I+1) and b(I+1), each -1 or +1
    length(As, L),
    length(Bs, L),
    append(As, Bs, Vars),
    maplist([X]>>(X in (-1) \/ 1), Vars),
    % the values of A sum to 1, and the values of B sum to 1
    sum(As, #=, 1),
    sum(Bs, #=, 1),
    % for each shift, the periodic autocorrelations of A and B add up to -2
    numlist(1, Shifts, Lags),
    maplist({As, Bs, L}/[S]>>correlated(As, Bs, L, S), Lags).

correlated(As, Bs, L, S) :-
    periodic(As, L, S, First),
    periodic(Bs, L, S, Second),
    First + Second #= -2.

% PAF(Xs, S): the sum over I of x_I * x_((I+S) mod L), counted from 1
periodic(Xs, L, S, Total) :-
    numlist(1, L, Positions),
    maplist({Xs, L, S}/[I, Product]>>shifted_product(Xs, L, S, I, Product), Positions, Products),
    sum(Products, #=, Total).

shifted_product(Xs, L, S, I, Product) :-
    nth1(I, Xs, Here),
    J is ((I - 1 + S) mod L) + 1,
    nth1(J, Xs, There),
    Product #= Here * There.

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

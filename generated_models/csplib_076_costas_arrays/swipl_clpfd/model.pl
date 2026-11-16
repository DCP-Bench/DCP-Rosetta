% csplib_076_costas_arrays: a SWI-Prolog model from DCP Rosetta.
%
% A Costas array is a pattern of n marks on an n x n grid, one mark per row and one per column, in which the n(n-1)/2
% vectors between the marks are all different. Such patterns are important as they provide a template for generating
% radar and sonar signals with ideal ambiguity functions.
%
% A model for the Costas Array Problem (CAP) is to define an array of variables X1, ..., Xn which form a permutation.
% For each length l in 1, ..., n-1, we add n-l more variables, each assigned the difference Xi - Xi+l for i in 1, ...,
% n-l. These additional variables form a difference triangle. Each line of this difference triangle must not contain
% any value twice: the CAP is a collection of all-different constraints on X1, ..., Xn and on the lines of the
% difference triangle.
%
% Save this file as model.pl. Download `csplib_076_costas_arrays.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_076_costas_arrays.json')" -t halt model.pl
%
% Data fields: n (the order of the array: the permutation holds the values 1 to n).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, [Costas, Triangle], [costas-Costas]) :-
    N = Instance.n,
    Last is N - 1,
    % Costas[I] is the value in position I, counted from 1: a permutation of 1..N
    length(Costas, N),
    Costas ins 1..N,
    all_distinct(Costas),
    % one line of the difference triangle for each lag from 1 to N-1
    findall(L, between(1, Last, L), Lags),
    maplist({Costas, N}/[L, Row]>>difference_row(Costas, N, L, Row), Lags, Triangle).

% the differences Costas[I] - Costas[I+L] for I from 1 to N-L are all different
difference_row(Costas, N, L, Row) :-
    Count is N - L,
    numlist(1, Count, Starts),
    maplist({Costas, L}/[I, D]>>(I2 is I + L, nth1(I, Costas, A), nth1(I2, Costas, B), D #= A - B),
            Starts, Row),
    all_distinct(Row).

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

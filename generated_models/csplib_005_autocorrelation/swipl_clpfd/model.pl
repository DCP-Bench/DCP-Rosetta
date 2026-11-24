% csplib_005_autocorrelation: a SWI-Prolog model from DCP Rosetta.
%
% Construct a binary sequence of length n that minimizes the autocorrelations between bits. Each bit takes the value
% +1 or -1. With periodic (cyclic) boundary conditions, the k-th autocorrelation is
%
%     C_k = sum over i from 0 to n-1 of S_i * S_((i+k) mod n)
%
% and the aim is to minimize the sum of their squares, E = sum over k from 1 to n-1 of C_k^2.
%
% Save this file as model.pl. Download `csplib_005_autocorrelation.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_005_autocorrelation.json')" -t halt model.pl
%
% Data fields: n (the length of the sequence).
:- use_module(library(clpfd)).

model(Instance, Vars, [sequence-Sequence], min(Energy)) :-
    N = Instance.n,
    Last is N - 1,
    % Sequence[I] is bit I, +1 or -1
    length(Sequence, N),
    Sequence ins -1..1,
    maplist(bit, Sequence),
    % the energy is the sum of the squared autocorrelations for the shifts 1 to n-1
    numlist(1, Last, Shifts),
    maplist(squared_correlation(Sequence), Shifts, Squares),
    sum(Squares, #=, Energy),
    Vars = [Sequence, Energy].

% each bit is +1 or -1, not 0
bit(S) :-
    S #\= 0.

% C_K is the sum of S_I * S_((I+K) mod N), and Square is C_K squared
squared_correlation(Sequence, Shift, Square) :-
    rotated(Sequence, Shift, Shifted),
    maplist(times, Sequence, Shifted, Products),
    sum(Products, #=, Correlation),
    Square #= Correlation * Correlation.

% Shifted[I] is Sequence[(I+Shift) mod N]: the sequence rotated left by Shift
rotated(Sequence, Shift, Shifted) :-
    length(Front, Shift),
    append(Front, Back, Sequence),
    append(Back, Front, Shifted).

times(A, B, Product) :-
    Product #= A * B.

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

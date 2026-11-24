% csplib_049_number_partitioning: a SWI-Prolog model from DCP Rosetta.
%
% Partition the numbers 1 to N into two sets A and B such that A and B have the same cardinality, the sum of the
% numbers in A equals the sum of the numbers in B, and the sum of their squares in A equals that in B. There is no
% solution for N < 8.
%
% Save this file as model.pl. Download `csplib_049_number_partitioning.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_049_number_partitioning.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_049_number_partitioning.json')" -t halt model.pl
%
% Data fields: n (the largest number N).
:- use_module(library(clpfd)).

model(Instance, Vars, ['A'-A, 'B'-B]) :-
    N = Instance.n,
    0 =:= N mod 2,                            % the two sets have the same size only when N is even
    K is N // 2,                              % the size of each set
    length(A, K), length(B, K),
    append(A, B, Numbers),
    % every number from 1 to N is in exactly one of the sets
    Numbers ins 1..N,
    all_distinct(Numbers),
    % each set listed in increasing order
    chain(A, #<), chain(B, #<),
    % the sums of the numbers are equal
    sum(A, #=, SumA), sum(B, #=, SumB),
    SumA #= SumB,
    % the sums of the squares are equal
    maplist(square, A, SquaresA), maplist(square, B, SquaresB),
    sum(SquaresA, #=, QA), sum(SquaresB, #=, QB),
    QA #= QB,
    Vars = Numbers.

square(X, Y) :- Y #= X*X.

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

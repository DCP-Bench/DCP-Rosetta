% csplib_019_magic_squares_and_sequences: a SWI-Prolog model from DCP Rosetta.
%
% A magic sequence of length n is a sequence of integers x_0, ..., x_(n-1), each between 0 and n-1, such that for every
% i from 0 to n-1 the number i occurs exactly x_i times in the sequence. For example, 6, 2, 1, 0, 0, 0, 1, 0, 0, 0 is a
% magic sequence of length 10, since 0 occurs 6 times in it, 1 occurs twice, and so on.
%
% Save this file as model.pl. Download `csplib_019_magic_squares_and_sequences.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_019_magic_squares_and_sequences.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_019_magic_squares_and_sequences.json')" -t halt model.pl
%
% Data fields: n (the length of the sequence).
:- use_module(library(clpfd)).

model(Instance, Vars, [x-X]) :-
    N = Instance.n,
    Last is N - 1,
    % X[I] is the number of times the value I occurs in the sequence
    length(X, N),
    X ins 0..Last,
    Vars = X,
    % the value I occurs exactly X[I] times in the sequence
    numlist(0, Last, Keys),
    pairs_keys_values(Counts, Keys, X),
    global_cardinality(X, Counts).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
:- use_module(library(http/json)).
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

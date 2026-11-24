% session2_subsets_100: a SWI-Prolog model from DCP Rosetta.
%
% From a set A of different integers one can always find two disjoint non-empty subsets S and T whose elements have
% the same sum. S union T need not be all of A. Find sets S and T for the given set A.
%
% Save this file as model.pl. Download `session2_subsets_100.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('session2_subsets_100.json')" -t halt model.pl
%
% Data fields: A (the integers of the set, lists indexed from 0).
:- use_module(library(clpfd)).

model(Instance, [InS, InT], [in_S-InS, in_T-InT]) :-
    get_dict('A', Instance, A),
    length(A, N),                          % the number of integers in A
    length(InS, N), InS ins 0..1,          % InS[I] = 1 when element I is in S
    length(InT, N), InT ins 0..1,          % InT[I] = 1 when element I is in T
    % S and T are both non-empty
    sum(InS, #>=, 1),
    sum(InT, #>=, 1),
    % no element is in both S and T
    maplist(disjoint, InS, InT),
    % the elements of S and the elements of T have the same sum
    scalar_product(A, InS, #=, SumS),
    scalar_product(A, InT, #=, SumT),
    SumS #= SumT.

disjoint(S, T) :- S + T #=< 1.

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

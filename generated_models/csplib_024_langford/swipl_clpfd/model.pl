% csplib_024_langford: a SWI-Prolog model from DCP Rosetta.
%
% Langford's problem: take two copies of each number from 1 to k and arrange the 2k numbers in one sequence, so
% that the two copies of each number I have exactly I numbers between them.
%
% Save this file as model.pl. Download `csplib_024_langford.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_024_langford.json')" -t halt model.pl
%
% Data fields: k (the largest number; the sequence has 2k numbers).
:- use_module(library(clpfd)).

model(Instance, Vars, [sol-Sol]) :-
    K = Instance.k,
    N2 is 2*K,                              % the length of the sequence
    length(Sol, N2),
    Sol ins 1..K,                           % Sol[P] is the number at position P (positions from 1)
    numlist(1, K, Numbers),
    length(First, K), length(Second, K),    % the positions of the two copies of each number
    First ins 1..N2, Second ins 1..N2,
    % the two copies of number I have exactly I numbers between them
    maplist(apart, Numbers, First, Second),
    % every position holds exactly one number
    append(First, Second, Vars),
    all_distinct(Vars),
    % the two copies of number I stand at positions where Sol is I
    maplist(place(Sol), Numbers, First, Second).

apart(I, F, S) :- S #= F + I + 1.

place(Sol, I, F, S) :- element(F, Sol, I), element(S, Sol, I).

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

% three_sum: a SWI-Prolog model from DCP Rosetta.
%
% Given a collection of integers, find exactly `m` elements that sum to zero.
%
% Save this file as model.pl. Download `three_sum.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('three_sum.json')" -t halt model.pl
%
% Data fields: m (how many numbers to pick) and nums (the integers, a list indexed from 0).
:- use_module(library(clpfd)).

model(Instance, Selected, [indices-Selected]) :-
    Nums = Instance.nums,
    M = Instance.m,
    length(Nums, N),
    length(Selected, N),                  % one 0/1 flag per number
    Selected ins 0..1,                    % Selected[I] = 1 when number I is picked
    % exactly m numbers are picked
    sum(Selected, #=, M),
    % the picked numbers add up to zero
    scalar_product(Nums, Selected, #=, 0).

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

% knapsack: a SWI-Prolog model from DCP Rosetta.
%
% A hiker is planning a trip and needs to decide which items to take in their backpack. Each item has a certain
% value and weight, and the hiker wants to maximize the total value of the items in the backpack without exceeding
% the weight capacity of the backpack.
%
% Save this file as model.pl. Download `knapsack.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/knapsack.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('knapsack.json')" -t halt model.pl
%
% Data fields: capacity (the weight capacity of the backpack), values and weights (value and weight of each item,
% lists indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(http/json)).

model(Instance, X, [x-X], max(Value)) :-
    Capacity = Instance.capacity,
    length(Instance.values, N),            % the number of items
    length(X, N),
    X ins 0..1,                            % X[I] = 1 when item I is taken
    % the items taken weigh no more than the capacity of the backpack
    scalar_product(Instance.weights, X, #=<, Capacity),
    % maximise the total value of the items taken
    scalar_product(Instance.values, X, #=, Value).

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

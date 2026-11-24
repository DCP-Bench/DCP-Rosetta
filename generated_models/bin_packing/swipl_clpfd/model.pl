% bin_packing: a SWI-Prolog model from DCP Rosetta.
%
% Given several items of specific weights and a number of bins of a fixed capacity, assign each item to a bin so
% that the total weight of the items in each bin does not exceed the capacity.
%
% Save this file as model.pl. Download `bin_packing.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('bin_packing.json')" -t halt model.pl
%
% Data fields: capacity (the capacity of each bin), num_bins (the number of bins), weights (the weight of each
% item, lists indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).
:- use_module(library(http/json)).

model(Instance, Bins, [bins-Bins]) :-
    Capacity = Instance.capacity,
    NumBins = Instance.num_bins,
    Weights = Instance.weights,
    length(Weights, N),                    % the number of items
    length(Bins, N),
    Last is NumBins - 1,
    Bins ins 0..Last,                      % Bins[I] is the bin item I is assigned to
    % the total weight of the items in each bin does not exceed the capacity
    numlist(0, Last, BinIds),
    maplist(fits(Bins, Weights, Capacity), BinIds).

% the items assigned to bin B weigh no more than the capacity
fits(Bins, Weights, Capacity, B) :-
    maplist({B}/[Bi, Here]>>(Bi #= B #<==> Here), Bins, Heres),
    scalar_product(Weights, Heres, #=<, Capacity).

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

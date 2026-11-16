% twelve_pack: a SWI-Prolog model from DCP Rosetta.
%
% Given a target number of items, find the combination of packs of different sizes whose total number of items is
% at least the target and as close to it as possible.
%
% Save this file as model.pl. Download `twelve_pack.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('twelve_pack.json')" -t halt model.pl
%
% Data fields: target (the number of items wanted) and packs (the number of items in each pack size, a list
% indexed from 0).
:- use_module(library(clpfd)).

model(Instance, Vars, [counts-Counts], min(Total)) :-
    Target = Instance.target,
    Packs = Instance.packs,
    length(Packs, N),
    length(Counts, N),                    % Counts[I] = how many packs of size Packs[I] are bought
    % a count above the target is never optimal: one pack fewer would still reach the target
    Counts ins 0..Target,
    % the number of items in all the packs bought
    scalar_product(Packs, Counts, #=, Total),
    % at least the target number of items
    Total #>= Target,
    % the total is the auxiliary variable that is minimised, so it is labelled too
    Vars = [Total|Counts].

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

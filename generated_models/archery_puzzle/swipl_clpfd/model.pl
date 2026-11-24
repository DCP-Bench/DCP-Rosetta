% archery_puzzle: a SWI-Prolog model from DCP Rosetta.
%
% How close can the young archer come to scoring a total of a target score using as many arrows as she pleases? The
% targets are given as a list of integers, and each may be hit any number of times. Her score is the sum of the values
% of all her hits, and the aim is to minimize the absolute difference between that score and the target score.
%
% Save this file as model.pl. Download `archery_puzzle.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('archery_puzzle.json')" -t halt model.pl
%
% Data fields: target_score (the target score), targets (the value of a hit on each target, a list indexed from 0).
:- use_module(library(clpfd)).

model(Instance, Vars, [hits-Hits], min(Gap)) :-
    Targets = Instance.targets,
    Goal = Instance.target_score,
    length(Targets, N),
    length(Hits, N),
    % the best score is never more than the target plus the largest value of a hit, so no target needs more hits
    % than that bound allows
    max_list(Targets, Largest),
    Limit is Goal + Largest,
    maplist(bounded_hits(Limit), Targets, Hits),
    % the score is the sum of the values of all the hits
    scalar_product(Targets, Hits, #=, Score),
    % the gap between the score and the target score, to be minimised
    Gap #= abs(Score - Goal),
    append([Hits, [Score, Gap]], Vars).

% the hits on a target, each of value Value, do not reach beyond the limit
bounded_hits(Limit, Value, Hit) :-
    Hit in 0..Limit,
    Hit * Value #=< Limit.

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

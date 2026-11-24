% broken_weights: a SWI-Prolog model from DCP Rosetta.
%
% A merchant's measuring weight broke into a number of pieces, each a whole number of pounds. The pieces can be used on
% a balance scale to weigh every whole number of pounds from 1 up to the total weight: a piece may go on either pan
% or be left off the scale. For example, a 1-pound and a 4-pound piece weigh a 3-pound object, with the object and the
% 1-pound piece on one pan and the 4-pound piece on the other. Find the weights of the pieces.
%
% Save this file as model.pl. Download `broken_weights.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('broken_weights.json')" -t halt model.pl
%
% Data fields: m (the total weight, in pounds), n (the number of pieces).
:- use_module(library(clpfd)).

model(Instance, Vars, [weights-Weights]) :-
    M = Instance.m,
    N = Instance.n,
    length(Weights, N),                     % the weight of each piece
    Weights ins 1..M,
    sum(Weights, #=, M),                    % the pieces make up the total weight
    chain(Weights, #=<),                    % symmetry breaking, not in the statement: the pieces are listed in ascending weight
    % each whole weight T from 1 to M is weighed by some placement of the pieces
    numlist(1, M, Targets),
    maplist(weighable(Weights), Targets, Placements),
    append([Weights|Placements], Vars).

% The pieces (with weights Weights) can weigh Target: Placement gives each piece -1 when it is on the object's pan,
% 1 when it is on the other pan and 0 when it is off the scale, and the pieces on the other pan outweigh those with the
% object by Target.
weighable(Weights, Target, Placement) :-
    length(Weights, N),
    length(Placement, N),
    Placement ins -1..1,
    maplist(on_pan, Placement, Weights, Contributions),   % each piece contributes its signed weight
    sum(Contributions, #=, Target).

% Contribution is the signed weight of one piece (Side is its placement, Weight its weight).
on_pan(Side, Weight, Contribution) :-
    Contribution #= Side * Weight.

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

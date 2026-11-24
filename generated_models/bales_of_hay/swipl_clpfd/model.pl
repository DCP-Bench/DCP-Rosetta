% bales_of_hay: a SWI-Prolog model from DCP Rosetta.
%
% A number of bales of hay were weighed in every possible combination of two bales. The weights of these pairs were
% written down in numerical order, without recording which pair gave which weight. Find the weight of each bale.
%
% Save this file as model.pl. Download `bales_of_hay.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('bales_of_hay.json')" -t halt model.pl
%
% Data fields: n (the number of bales), weights (the weights of the pairs of bales, in numerical order).
:- use_module(library(clpfd)).

model(Instance, Vars, [bales-Bales]) :-
    N = Instance.n,
    Weights = Instance.weights,
    length(Weights, Pairs),                 % one weight for each pair of bales
    length(Bales, N),
    max_list(Weights, Heaviest),
    Bales ins 0..Heaviest,                  % no bale is heavier than the heaviest pair
    % the pairs of bales I < J, in a fixed order
    findall(I-J, (between(1, N, I), I1 is I + 1, between(I1, N, J)), PairList),
    % each pair is matched with a different weight of the list
    length(Matches, Pairs),
    Matches ins 1..Pairs,
    all_distinct(Matches),
    maplist(pair_weight(Bales, Weights), PairList, Matches),
    append([Bales, Matches], Vars).

% The two bales of pair I-J weigh together the weight in position Match of the list.
pair_weight(Bales, Weights, I-J, Match) :-
    nth1(I, Bales, BaleI),
    nth1(J, Bales, BaleJ),
    element(Match, Weights, Weight),
    BaleI + BaleJ #= Weight.

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

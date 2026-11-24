% set_game: a SWI-Prolog model from DCP Rosetta.
%
% Set is a card game with a deck of 81 unique cards, each with four features (number, shading, color and shape), each
% feature having three possible values. Three cards form a "set" when, for each of the four features, the three cards
% show that feature either all the same or all different. Given a list of cards, each written as
% [number, shading, color, shape], find three different cards that form a set.
%
% Save this file as model.pl. Download `set_game.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('set_game.json')" -t halt model.pl
%
% Data fields: cards_data (the cards, each a list of its four feature values as numbers 1..3, in the order number,
% shading, color, shape; lists indexed from 0). The other fields name the values of each feature.
:- use_module(library(clpfd)).

model(Instance, [Winners, Positions], [winning_cards-Winners]) :-
    Cards = Instance.cards_data,
    length(Cards, N),                      % the number of cards on the table
    length(Winners, 3),
    Last is N - 1,
    Winners ins 0..Last,                   % the 0-based index of each card in the set
    all_different(Winners),
    maplist(one_based, Winners, Positions),
    % for each of the four features, the three cards are all the same or all different in that feature
    numlist(1, 4, Features),
    maplist(feature_is_set(Cards, Positions), Features).

one_based(Index, Position) :- Position #= Index + 1.

feature_is_set(Cards, Positions, Feature) :-
    maplist(nth1(Feature), Cards, Column),
    maplist(value_at(Column), Positions, [V1, V2, V3]),
    (   V1 #= V2 #/\ V2 #= V3
    ;   V1 #\= V2 #/\ V2 #\= V3 #/\ V1 #\= V3
    ).

value_at(Column, Position, Value) :- element(Position, Column, Value).

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

% set_game: an ECLiPSe model from DCP Rosetta.
%
% Set is a card game with 81 unique cards, each with four features (number, shading, color and shape), each
% feature having three possible values. Three cards form a set when, for each of the four features, the three
% cards are either all the same or all different. Given a list of cards, each written as [number, shading,
% color, shape], find three different cards that form a set.
%
% Save this file as model.ecl. Download `set_game.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py set_game.json
%   eclipse -b model.ecl -e "run('set_game_1.dat'), halt"

% cards_data: the cards, indexed from 0 as in the JSON, each written [number, shading, color, shape] with each feature 1, 2 or 3.
% The other fields name these values and are not read.

:- lib(ic).
:- lib(listut).

% Winning: the cards of the set, by their position in the list counted from 1 (I1 to I3)
% and reported as 0-based indices (W1 to W3).
model(Instance, [I1, I2, I3], [winning_cards-[W1, W2, W3]]) :-
    memberchk(cards_data-Cards, Instance),
    length(Cards, NC),
    [I1, I2, I3] :: 1..NC,
    % three different cards
    alldifferent([I1, I2, I3]),
    % for each of the four features, the three cards show the feature all the same or all different
    ( for(F, 1, 4), param(Cards, I1, I2, I3) do
        feature_column(Cards, F, Column),
        element(I1, Column, V1),
        element(I2, Column, V2),
        element(I3, Column, V3),
        % the number of pairs of cards that agree on the feature is 3 (all the same) or 0 (all different);
        % 1 would mean two cards agree and the third differs, and 2 is impossible
        E12 #= (V1 #= V2),
        E23 #= (V2 #= V3),
        E13 #= (V1 #= V3),
        E12 + E23 + E13 #\= 1
    ),
    W1 #= I1 - 1,
    W2 #= I2 - 1,
    W3 #= I3 - 1.

% Column: the value of feature F on every card
feature_column(Cards, F, Column) :-
    ( foreach(Card, Cards), foreach(V, Column), param(F) do
        nth1(F, Card, V)
    ).

:- lib(branch_and_bound).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_module(gfd) -> Lib = gfd ; Lib = ic ),
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   Objective = max(Expr)
    ->  call(Lib:(Total #= Expr)), call(Lib:(Cost #= -Total)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   Objective = min(Expr)
    ->  call(Lib:(Cost #= Expr)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   run_search(Vars, Outputs)
    ),
    ( foreach(Name-Value, Outputs) do printf("%w = %w%n", [Name, Value]) ).

run_search(Vars, Outputs) :-
    (   current_predicate(search_goal/1) -> search_goal(Vars) ; labeling(Vars) ),
    term_variables(Outputs, Free),
    labeling(Free).

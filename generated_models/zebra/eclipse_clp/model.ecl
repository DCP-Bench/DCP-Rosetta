% zebra: an ECLiPSe model from DCP Rosetta.
%
% The Zebra puzzle (sometimes referred to as Einstein's puzzle). There are five houses in a row, numbered from left to
% right. Each of the five houses is painted a different color, and has one inhabitant. The inhabitants are all of
% different nationalities, own different pets, drink different beverages and have different jobs. We know that: the
% painter owns the horse; the diplomat drinks coffee; the one who drinks milk lives in the white house; the Spaniard is
% a painter; the Englishman lives in the red house; the snails are owned by the sculptor; the green house is immediately
% on the left of the red one; the Norwegian lives immediately on the right of the blue house; the doctor drinks milk;
% the diplomat is Japanese; the Norwegian owns the zebra; the green house is next to the white one; the horse is owned
% by the neighbor of the diplomat; the Italian either lives in the red, white or green house.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% The puzzle has no data fields. Each output gives, for each item of its category in the order of the statement, the
% house number (0 to 4, from the left) of the inhabitant that has it.
:- lib(ic).

model(_Instance, Vars, [colors-Colors, nations-Nations, drinks-Drinks, jobs-Jobs, pets-Pets]) :-
    Colors = [Yellow, Green, Red, White, Blue],
    Nations = [Italy, Spain, Japan, England, Norway],
    Drinks = [Milk, Water, Tea, Coffee, Juice],
    Jobs = [Painter, Sculptor, Diplomat, Pianist, Doctor],
    Pets = [Cat, Zebra, Bear, Snails, Horse],
    % every category puts its five items in five different houses
    ( foreach(Category, [Colors, Nations, Drinks, Jobs, Pets]) do
        Category :: 0..4,
        alldifferent(Category)
    ),
    % the painter owns the horse
    Painter #= Horse,
    % the diplomat drinks coffee
    Diplomat #= Coffee,
    % the one who drinks milk lives in the white house
    Milk #= White,
    % the Spaniard is a painter
    Spain #= Painter,
    % the Englishman lives in the red house
    England #= Red,
    % the snails are owned by the sculptor
    Snails #= Sculptor,
    % the green house is immediately on the left of the red one
    Red #= Green + 1,
    % the Norwegian lives immediately on the right of the blue house
    Norway #= Blue + 1,
    % the doctor drinks milk
    Doctor #= Milk,
    % the diplomat is Japanese
    Diplomat #= Japan,
    % the Norwegian owns the zebra
    Norway #= Zebra,
    % the green house is next to the white one
    abs(Green - White) #= 1,
    % the horse is owned by the neighbor of the diplomat
    abs(Horse - Diplomat) #= 1,
    % the Italian either lives in the red, white or green house
    Italy #\= Yellow,
    Italy #\= Blue,
    join_lists(Colors, Nations, Items1),
    join_lists(Items1, Drinks, Items2),
    join_lists(Items2, Jobs, Items3),
    join_lists(Items3, Pets, Vars).

join_lists([], L, L).
join_lists([X|Xs], L, [X|Ys]) :-
    join_lists(Xs, L, Ys).

:- lib(branch_and_bound).

% Solves the model and prints each output.
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

run :- solve_model([]).

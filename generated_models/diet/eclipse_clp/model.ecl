% diet: an ECLiPSe model from DCP Rosetta.
%
% Given the prices and the nutritional requirements (at least) for each nutrition type, what is the optimal diet?
% The optimal diet minimizes the cost of the products, each bought in a whole number of units. The foods are a
% chocolate cake slice, a chocolate ice cream scoop, a bottle of cola and a pineapple cheesecake piece.
%
% Save this file as model.ecl. Download `diet.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/diet.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py diet.json
%   eclipse -b model.ecl -e "run('diet_1.dat'), halt"

% Data fields: n (the number of foods), price (the price of one unit of each food, a list indexed from 0),
% limits (the minimum required of calories, chocolate, sugar and fat, in that order).
% One unit of each food gives (calories, chocolate ounces, sugar ounces, fat ounces) as in the table:
% cake (400, 3, 2, 2), ice cream (200, 2, 2, 4), cola (150, 0, 4, 1), cheesecake (500, 0, 4, 5).

:- lib(ic).

model(Instance, Units, [cost-Cost], min(Cost)) :-
    memberchk(n-N, Instance),
    memberchk(price-Price, Instance),
    memberchk(limits-Limits, Instance),
    Limits = [MinCalories, MinChocolate, MinSugar, MinFat],
    length(Units, N),
    % the number of units of each food is a whole number; the largest requirement is an upper bound that loses no optimal diet (a unit beyond it could be dropped without breaking any requirement, and prices are not negative)
    Largest is max(max(MinCalories, MinChocolate), max(MinSugar, MinFat)),
    Units :: 0..Largest,
    Calories = [400, 200, 150, 500],
    Chocolate = [3, 2, 0, 0],
    Sugar = [2, 2, 4, 4],
    Fat = [2, 4, 1, 5],
    % the diet provides at least the required calories
    Calories * Units #>= MinCalories,
    % the diet provides at least the required chocolate
    Chocolate * Units #>= MinChocolate,
    % the diet provides at least the required sugar
    Sugar * Units #>= MinSugar,
    % the diet provides at least the required fat
    Fat * Units #>= MinFat,
    % the cost of the diet is the price of the units bought
    Cost #= Price * Units.

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

% birthday_coins: an ECLiPSe model from DCP Rosetta.
%
% Tommy was given 15 coins for his birthday. Each coin is a half-crown, a shilling or a sixpence, but he was not necessarily
% given coins of all three kinds. When he added them up, he found that he had one pound, five shillings and sixpence. A pound
% is 20 shillings, a shilling is 12 pence and a half-crown is 2 shillings and sixpence. How many half-crowns could he have
% been given?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/birthday_coins.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).

% Output half_crowns: the number of half-crowns, one of the possible answers.
model(_Instance, [HalfCrowns, Shillings, Sixpences], [half_crowns-HalfCrowns]) :-
    [HalfCrowns, Shillings, Sixpences] :: 0..15,
    % there are 15 coins in all
    HalfCrowns + Shillings + Sixpences #= 15,
    % the coins add up to 1 pound 5 shillings 6 pence: a half-crown is 30 pence, a shilling 12 and a sixpence 6,
    % and 1 pound 5 shillings 6 pence is 240 + 60 + 6 = 306 pence
    30 * HalfCrowns + 12 * Shillings + 6 * Sixpences #= 306.

:- lib(branch_and_bound).

% Builds the model, solves it and prints each output.
run :- solve_model([]).

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

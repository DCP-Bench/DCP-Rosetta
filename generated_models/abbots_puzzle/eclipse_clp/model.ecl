% abbots_puzzle: an ECLiPSe model from DCP Rosetta.
%
% If 100 bushels of corn were distributed among 100 people such that each man received three bushels, each woman
% two, and each child half a bushel, and there are five times as many women as men, find the number of men, women,
% and children.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% This problem has no instance data: the model reads nothing from the instance.
:- lib(ic).

model(_Instance, [Men, Women, Children], [men-Men, women-Women, children-Children]) :-
    % the number of men, women and children are not negative
    [Men, Women, Children] #:: 0..100,
    % the 100 people are men, women and children
    Men + Women + Children #= 100,
    % there are five times as many women as men
    Women #= 5 * Men,
    % the 100 bushels: each man gets 3, each woman 2 and each child half a bushel, so the bushels are
    % doubled to keep the arithmetic in integers
    6 * Men + 4 * Women + Children #= 200.

:- lib(branch_and_bound).

% Reads nothing, builds the model, solves it and prints each output.
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

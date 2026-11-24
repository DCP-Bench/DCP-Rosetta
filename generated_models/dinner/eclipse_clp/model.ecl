% dinner: an ECLiPSe model from DCP Rosetta.
%
% A father needs help with a math problem about going out to dinner. The family takes 1-6 grandparents,
% 1-10 parents and 1-40 children. Grandparents cost $3 for dinner, parents $2 and children $0.50. There must be
% 20 people at dinner in total, and the dinner must cost $20. Find how many grandparents, parents and children go.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% The model reads no data: the numbers are those of the problem.

:- lib(ic).

model(_Instance, Vars, [grandparents-G, parents-P, children-C]) :-
    Vars = [G, P, C],
    % 1 to 6 grandparents, 1 to 10 parents and 1 to 40 children go to dinner
    G :: 1..6,
    P :: 1..10,
    C :: 1..40,
    % there are 20 people at dinner in total
    G + P + C #= 20,
    % the dinner costs $20: in cents, grandparents 300 each, parents 200 each, children 50 each, total 2000
    300 * G + 200 * P + 50 * C #= 2000.

:- lib(branch_and_bound).

% Builds the model, solves it and prints each output.
run :-
    solve_model([]).

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

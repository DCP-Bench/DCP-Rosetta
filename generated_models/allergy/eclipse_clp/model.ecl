% allergy: an ECLiPSe model from DCP Rosetta.
%
% Four friends, two women named Debra and Janet and two men named Hugh and Rick, are each allergic to something
% different: eggs, mold, nuts or ragweed. Match each friend's surname (Baxter, Lemon, Malone or Fleet) with his or her
% allergy. Rick is not allergic to mold. Baxter is allergic to eggs. Hugh is neither surnamed Lemon nor Fleet. Debra
% is allergic to ragweed. Janet, who is not surnamed Lemon, is neither allergic to eggs nor to mold.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% This problem has no instance data: the model reads nothing from the instance.
% The friends are numbered Debra = 0, Janet = 1, Hugh = 2 and Rick = 3. Each surname and each allergy variable holds
% the number of the friend it belongs to.
:- lib(ic).

model(_Instance, Vars, [baxter-Baxter, eggs-Eggs, fleet-Fleet, lemon-Lemon, malone-Malone, mold-Mold, nuts-Nuts,
                        ragweed-Ragweed]) :-
    Vars = [Baxter, Lemon, Malone, Fleet, Eggs, Mold, Nuts, Ragweed],
    Vars :: 0..3,
    % each surname belongs to a different friend
    alldifferent([Baxter, Lemon, Malone, Fleet]),
    % each allergy belongs to a different friend
    alldifferent([Eggs, Mold, Nuts, Ragweed]),
    % Rick is not allergic to mold
    Mold #\= 3,
    % Baxter is allergic to eggs
    Baxter #= Eggs,
    % Hugh is neither surnamed Lemon nor Fleet
    Lemon #\= 2,
    Fleet #\= 2,
    % Debra is allergic to ragweed
    Ragweed #= 0,
    % Janet is not surnamed Lemon
    Lemon #\= 1,
    % Janet is neither allergic to eggs nor to mold
    Eggs #\= 1,
    Mold #\= 1.

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

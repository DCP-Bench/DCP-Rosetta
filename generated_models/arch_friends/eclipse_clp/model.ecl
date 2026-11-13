% arch_friends: an ECLiPSe model from DCP Rosetta.
%
% Harriet bought four pairs of shoes at four different stores: ecru espadrilles, fuchsia flats, purple pumps and
% suede sandals, at the Foot Farm, Heels in a Handcart, The Shoe Palace and Tootsies. Find the order in which she
% bought the pairs, and where she bought each one. Harriet bought fuchsia flats at Heels in a Handcart. The store she
% visited just after buying her purple pumps was not Tootsies. The Foot Farm was her second stop. Two stops after
% leaving The Shoe Palace, she bought her suede sandals.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% This problem has no instance data: the model reads nothing from the instance.
% Each shoe and each store variable holds the stop, from 1 to 4, at which that shoe was bought or that store was visited.
:- lib(ic).

model(_Instance, Vars, [ecruespadrilles-Ecru, fuchsiaflats-Fuchsia, purplepumps-Purple, suedesandals-Suede,
                        footfarm-FootFarm, heelsinahandcart-Heels, theshoepalace-Palace, tootsies-Tootsies]) :-
    Vars = [Ecru, Fuchsia, Purple, Suede, FootFarm, Heels, Palace, Tootsies],
    Vars :: 1..4,
    % each shoe is bought at a different stop
    alldifferent([Ecru, Fuchsia, Purple, Suede]),
    % each store is visited at a different stop
    alldifferent([FootFarm, Heels, Palace, Tootsies]),
    % Harriet bought fuchsia flats at Heels in a Handcart
    Fuchsia #= Heels,
    % the store visited just after buying purple pumps exists, and it was not Tootsies
    Purple #< 4,
    Tootsies #\= Purple + 1,
    % The Foot Farm was the second stop
    FootFarm #= 2,
    % two stops after leaving The Shoe Palace, she bought suede sandals
    Suede #= Palace + 2.

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

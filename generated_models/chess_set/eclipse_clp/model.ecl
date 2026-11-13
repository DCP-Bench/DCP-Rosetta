% chess_set: an ECLiPSe model from DCP Rosetta.
%
% A small joinery makes two sizes of boxwood chess sets, a small set and a large set. A small set needs 3 hours of
% lathe machining and 1 kg of boxwood, a large set needs 2 hours and 3 kg. There are four lathes, each worked 40 hours a
% week, so 160 lathe-hours are available a week, and only 200 kg of boxwood a week can be obtained. A large set yields a
% profit of $20 and a small set a profit of $5. The joinery wants to decide how many sets of each kind to make each week
% so as to maximize its profit.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/chess_set.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"
%
% This problem has no data fields: the numbers above are part of the model.
:- lib(ic).
:- lib(branch_and_bound).

% Outputs: small_set and large_set (the numbers of sets made) and max_profit (the profit they yield).
model(_Instance, [S, L, P], [small_set-S, large_set-L, max_profit-P], max(P)) :-
    % the number of sets of each kind is not negative and no more than the boxwood allows
    [S, L] :: 0..200,
    % lathe time: 3 hours per small set and 2 hours per large set, at most 160 hours a week
    3 * S + 2 * L #=< 160,
    % boxwood: 1 kg per small set and 3 kg per large set, at most 200 kg a week
    S + 3 * L #=< 200,
    % profit: $5 per small set and $20 per large set
    P #= 5 * S + 20 * L.

% Reads the data file, builds the model, solves it and prints each output.
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

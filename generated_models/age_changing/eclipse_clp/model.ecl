% age_changing: an ECLiPSe model from DCP Rosetta.
%
% Start with my age, in years, and apply the four operations +2, /8, -3 and *7 in some order: the final answer is my
% husband's age. Start with his age and apply the same four operations in a different order: the final answer is my
% age. Both ages are between 16 and 120, and every intermediate result is a positive integer, so a division by 8 must
% be exact. What are our two ages?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% This problem has no instance data: the model reads nothing from the instance.
% M is my age and H is my husband's age.
:- lib(ic).

model(_Instance, [M, H], [m-M, h-H]) :-
    % both ages are between 16 and 120
    M #:: 16..120,
    H #:: 16..120,
    % the four operations, each used once
    Ops = [plus2, div8, minus3, times7],
    % the order in which the operations are applied to my age to get his
    age_order(Ops, Order1),
    % a different order of the same operations applied to his age to get mine
    age_order(Ops, Order2),
    Order1 \== Order2,
    age_chain(Order1, M, H),
    age_chain(Order2, H, M).

% apply the steps of an order, one after the other, from the start value X to the final value Y
age_chain([], X, X).
age_chain([Op | Ops], X, Y) :-
    age_step(Op, X, Z),
    age_chain(Ops, Z, Y).

% each step gives a positive integer; a division by 8 must be exact
age_step(plus2, X, Z) :- Z #= X + 2, Z #>= 1.
age_step(div8, X, Z) :- X #= 8 * Z, Z #>= 1.
age_step(minus3, X, Z) :- Z #= X - 3, Z #>= 1.
age_step(times7, X, Z) :- Z #= 7 * X, Z #>= 1.

% an order of the operations: the list Ys is Xs in some order
age_order([], []).
age_order(Xs, [X | Ys]) :-
    age_pick(X, Xs, Rest),
    age_order(Rest, Ys).

age_pick(X, [X | Xs], Xs).
age_pick(X, [Y | Xs], [Y | Ys]) :-
    age_pick(X, Xs, Ys).

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

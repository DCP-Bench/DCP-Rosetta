% session5_hardy_1729_square: an ECLiPSe model from DCP Rosetta.
%
% Find four different numbers a, b, c and d, each between 1 and 100, such that the sum of the squares of a and b
% equals the sum of the squares of c and d: a^2 + b^2 = c^2 + d^2.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% The model reads no data: the four numbers are its variables.

:- lib(ic).

% A, B, C and D: the four numbers, each from 1 to 100, all different.
model(_Instance, [A, B, C, D], [a-A, b-B, c-C, d-D]) :-
    [A, B, C, D] :: 1..100,
    alldifferent([A, B, C, D]),
    % the sum of the squares of a and b equals the sum of the squares of c and d
    A * A + B * B #= C * C + D * D.

:- lib(branch_and_bound).

% Solves the model and prints each output.
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

% pythagorean_triplet: an ECLiPSe model from DCP Rosetta.
%
% A Pythagorean triplet is a set of three natural numbers a, b and c for which a^2 + b^2 = c^2. The order of a and b
% does not matter. Find the Pythagorean triplet for which a + b + c = 1000.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).
:- lib(branch_and_bound).

% Outputs a, b and c: the three natural numbers, with a < b since the order of a and b does not matter.
model(_Instance, Vars, [a-A, b-B, c-C]) :-
    Perimeter is 1000,
    Vars = [A, B, C],
    [A, B, C] :: 1..Perimeter,

    % a + b + c is the perimeter
    A + B + C #= Perimeter,

    % a^2 + b^2 = c^2
    A * A + B * B #= C * C,

    % the order of a and b does not matter, so a is the smaller one
    A #< B.

% the search picks the variable with the fewest candidate values first and tries the lowest value first
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% Reads no data, builds the model, solves it and prints each output.
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

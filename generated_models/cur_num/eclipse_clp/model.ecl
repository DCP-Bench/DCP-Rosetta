% cur_num: an ECLiPSe model from DCP Rosetta.
%
% The number 48 has this peculiarity: if you add 1 to it the result is a square number, and if you add 1 to its half
% you also get a square number. Find another number with this peculiarity between 1 and 10000.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).

% Peculiar is the number, Half its half, A and B the square roots of Peculiar+1 and Half+1.
model(_Instance, [Peculiar, Half, A, B], [peculiar-Peculiar]) :-
    % a number between 1 and 10000, other than 48 itself
    Peculiar :: 1..10000,
    Peculiar #\= 48,

    % the half of the number is an integer, so the number is even
    Half :: 1..5000,
    Peculiar #= 2 * Half,

    % adding 1 to the number gives a square number
    A :: 1..100,
    A * A #= Peculiar + 1,

    % adding 1 to its half gives a square number
    B :: 1..70,
    B * B #= Half + 1.

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

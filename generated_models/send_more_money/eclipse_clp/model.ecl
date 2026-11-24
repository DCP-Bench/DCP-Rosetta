% send_more_money: an ECLiPSe model from DCP Rosetta.
%
% The "Send More Money" puzzle is a classic cryptarithmetic problem where each letter represents a unique digit. The
% goal is to assign digits to the letters such that SEND + MORE = MONEY holds true, where each letter must be assigned
% a unique digit from 0 to 9, and the first letter of each word cannot be zero.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% No data fields: the model reads no data, so the run block calls it with an empty list.
:- lib(ic).

% Outputs d, e, m, n, o, r, s, y: the digit of each letter.
model(_Data, Vars, [d-D, e-E, m-M, n-N, o-O, r-R, s-S, y-Y]) :-
    Vars = [S, E, N, D, M, O, R, Y],
    Vars :: 0..9,

    % each letter stands for a different digit
    alldifferent(Vars),

    % the first letter of each word is not zero
    S #\= 0,
    M #\= 0,

    % SEND + MORE = MONEY
    1000*S + 100*E + 10*N + D + 1000*M + 100*O + 10*R + E #=
        10000*M + 1000*O + 100*N + 10*E + Y.

:- lib(branch_and_bound).

% Solves the model and prints each output.
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

% five_statements: an ECLiPSe model from DCP Rosetta.
%
% Determine which of the following statements is true.
%   1. Exactly one of these statements is false.
%   2. Exactly two of these statements are false.
%   3. Exactly three of these statements are false.
%   4. Exactly four of these statements are false.
%   5. Exactly five of these statements are false.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

:- lib(ic).

% S1 to S5 are the statements, 1 when the statement is true and 0 when it is false; F is the number of false statements.
model(_Instance, [S1, S2, S3, S4, S5, F], [statements-[S1, S2, S3, S4, S5]]) :-
    [S1, S2, S3, S4, S5] :: 0..1,
    F :: 0..5,

    % the number of false statements is the number of statements whose value is 0
    F #= 5 - (S1 + S2 + S3 + S4 + S5),

    % statement i is true exactly when exactly i of the statements are false
    S1 #= (F #= 1),
    S2 #= (F #= 2),
    S3 #= (F #= 3),
    S4 #= (F #= 4),
    S5 #= (F #= 5).

% Builds the model, solves it and prints each output.
run :- solve_model([]).

:- lib(branch_and_bound).

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

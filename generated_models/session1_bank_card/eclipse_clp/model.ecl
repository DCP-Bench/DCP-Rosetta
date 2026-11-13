% session1_bank_card: an ECLiPSe model from DCP Rosetta.
%
% My bank card has a 4 digit pin, abcd. I use the following facts to help me remember it: no two digits are the same,
% the 2-digit number cd is 3 times the 2-digit number ab, and the 2-digit number da is 2 times the 2-digit number bc.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% No data fields: the model reads no data, so the run block calls it with an empty list.
:- lib(ic).

% Outputs a, b, c, d: the digits of the PIN abcd.
model(_Data, Vars, [a-A, b-B, c-C, d-D]) :-
    Vars = [A, B, C, D],
    Vars :: 0..9,

    % no two digits are the same
    alldifferent(Vars),

    % the 2-digit number cd is 3 times the 2-digit number ab
    10*C + D #= 3*(10*A + B),

    % the 2-digit number da is 2 times the 2-digit number bc
    10*D + A #= 2*(10*B + C).

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

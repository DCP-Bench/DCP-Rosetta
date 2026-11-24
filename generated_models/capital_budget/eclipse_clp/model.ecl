% capital_budget: an ECLiPSe model from DCP Rosetta.
%
% A company considers a number of investments. Each investment yields a net present value (NPV) and requires a certain
% cash outflow at the present time. The total budget available for investment is limited. The company wants to choose
% investments so that the total NPV obtained is as large as possible without exceeding the budget.
%
% Save this file as model.ecl. Download `capital_budget.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/capital_budget.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py capital_budget.json
%   eclipse -b model.ecl -e "run('capital_budget_1.dat'), halt"
%
% Data fields: budget is the total budget available; cash_flow is the cash outflow of each investment and npv is its
% net present value (both lists indexed from 0 as in the JSON).
:- lib(ic).
:- lib(branch_and_bound).

% Outputs: x (whether each investment is chosen, 1 or 0) and z (the total NPV of the chosen investments).
model(Instance, Vars, [x-Xs, z-Z], max(Z)) :-
    memberchk(budget-Budget, Instance),
    memberchk(cash_flow-CashFlow, Instance),
    memberchk(npv-Npv, Instance),
    length(CashFlow, N),
    length(Xs, N),
    Xs :: 0..1,
    % the cash outflows of the chosen investments do not exceed the budget
    Spent #= CashFlow * Xs,
    Spent #=< Budget,
    % the total NPV of the chosen investments is to be maximized
    Z #= Npv * Xs,
    append(Xs, [Spent, Z], Vars).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

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

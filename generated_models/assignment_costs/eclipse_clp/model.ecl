% assignment_costs: an ECLiPSe model from DCP Rosetta.
%
% Assign people to 4 tasks, each with its own costs, so that the total cost is as small as possible. Each task must
% be assigned to exactly one person, but it is not necessary to assign all people to a task. X[I][J] is true when
% task I is assigned to person J, and false otherwise.
%
% Save this file as model.ecl. Download `assignment_costs.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py assignment_costs.json
%   eclipse -b model.ecl -e "run('assignment_costs_1.dat'), halt"

% Instance fields: cost (cost[I][J] is the cost of assigning task I to person J; a list of rows indexed from 0).
:- lib(ic).
:- lib(listut).

model(Instance, Vars, [x-Rows], min(Total)) :-
    memberchk(cost-CostRows, Instance),
    length(CostRows, T),
    CostRows = [FirstRow | _],
    length(FirstRow, P),
    % one row per task, one 0/1 cell per person
    length(Rows, T),
    ( foreach(Row, Rows), param(P) do
        length(Row, P),
        Row :: 0..1
    ),
    concat_rows(Rows, Vars),
    % each task is assigned to exactly one person
    ( foreach(Row, Rows) do
        sum(Row) #= 1
    ),
    % each person takes at most one task
    ( for(J, 1, P), param(Rows) do
        person_column(Rows, J, Col),
        sum(Col) #=< 1
    ),
    % the total cost of the assignments made, to be minimised
    concat_rows(CostRows, FlatCost),
    Total #= FlatCost * Vars.

% the 1-based column J of a list of rows: the cells of one person across the tasks
person_column(Rows, J, Col) :-
    ( foreach(Row, Rows), foreach(X, Col), param(J) do
        nth1(J, Row, X)
    ).

% the rows of a list of rows, one after another
concat_rows([], []).
concat_rows([Row | Rows], Flat) :-
    concat_list(Row, Rest, Flat),
    concat_rows(Rows, Rest).

concat_list([], Ys, Ys).
concat_list([X | Xs], Ys, [X | Zs]) :- concat_list(Xs, Ys, Zs).

:- lib(branch_and_bound).

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

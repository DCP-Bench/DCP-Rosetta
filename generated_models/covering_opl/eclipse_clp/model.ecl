% covering_opl: an ECLiPSe model from DCP Rosetta.
%
% Select a set of workers to perform all the tasks, while minimizing the total hiring cost.
% Each worker has a hiring cost, and each task can be performed by certain workers.
% Every task must be performed.
%
% Save this file as model.ecl. Download `covering_opl.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py covering_opl.json
%   eclipse -b model.ecl -e "run('covering_opl_1.dat'), halt"

% Fields read from the data: nb_workers (the number of workers), Cost (the hiring cost of each worker, a list indexed from 0), and Qualified (for each
% task, a list indexed from 0 of the workers, numbered from 1, that can perform that task).

:- lib(ic).

model(Instance, Hired, [total_cost-Total, workers-Hired], min(Total)) :-
    memberchk(nb_workers-NbWorkers, Instance),
    memberchk('Cost'-Costs, Instance),
    memberchk('Qualified'-Qualified, Instance),
    length(Hired, NbWorkers),
    % each worker is either hired (1) or not (0)
    Hired :: 0..1,
    % every task is performed by at least one hired worker who is qualified for it
    ( foreach(Workers, Qualified), param(Hired) do
        ( foreach(W, Workers), foreach(H, Chosen), param(Hired) do
            element(W, Hired, H)
        ),
        sum(Chosen) #>= 1
    ),
    % the total hiring cost of the hired workers, to be minimized
    Total #= Costs * Hired.

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

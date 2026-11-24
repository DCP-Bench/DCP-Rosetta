% csplib_022_bus_driver_scheduling: an ECLiPSe model from DCP Rosetta.
%
% Find an optimal schedule for bus drivers. Given a set of tasks (pieces of work) to cover and a large set of possible
% shifts, where each shift covers a subset of the tasks, select a subset of shifts that covers each piece of work
% exactly once. Cover all tasks while minimising the total number of shifts used; the cost of each shift is the same.
%
% Save this file as model.ecl. Download `csplib_022_bus_driver_scheduling.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_022_bus_driver_scheduling.json
%   eclipse -b model.ecl -e "run('csplib_022_bus_driver_scheduling_1.dat'), halt"

% Instance fields: num_shifts (the number of shifts), num_work (the number of pieces of work, numbered from 0) and
% shifts (for each shift, the list of the pieces of work it covers, indexed from 0 as in the JSON).
% Output x: x[J] is 1 when shift J is selected, 0 otherwise.

:- lib(ic).

model(Instance, X, [x-X], min(sum(X))) :-
    memberchk(num_shifts-NS, Instance),
    memberchk(num_work-NW, Instance),
    memberchk(shifts-Shifts, Instance),
    % one 0/1 variable per shift
    length(X, NS),
    X :: 0..1,
    cover_all(0, NW, Shifts, X).

% each piece of work W is covered by exactly one selected shift
cover_all(W, NW, _, _) :-
    W >= NW, !.
cover_all(W, NW, Shifts, X) :-
    covering_vars(W, Shifts, X, Cov),
    sum(Cov) #= 1,
    W1 is W + 1,
    cover_all(W1, NW, Shifts, X).

% the variables of the shifts that contain the piece of work W
covering_vars(_, [], [], []).
covering_vars(W, [S|Ss], [V|Vs], Out) :-
    (   memberchk(W, S)
    ->  Out = [V|Out1]
    ;   Out = Out1
    ),
    covering_vars(W, Ss, Vs, Out1).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

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

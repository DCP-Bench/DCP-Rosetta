% resource_constrained_project_scheduling: an ECLiPSe model from DCP Rosetta.
%
% The resource-constrained project scheduling problem involves scheduling a set of jobs, each with a specific duration
% and resource requirement, such that the total project duration (makespan) is minimized. Each job may have precedence
% constraints, meaning certain jobs must be completed before others can start. Additionally, there are multiple types
% of resources, each with a limited capacity that must not be exceeded at any time. Given the durations of the jobs,
% their resource requirements, the capacities of the resources, and the precedence constraints between the jobs,
% determine the start times of the jobs that minimize the makespan while satisfying all constraints.
%
% Save this file as model.ecl. Download `resource_constrained_project_scheduling.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/resource_constrained_project_scheduling.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py resource_constrained_project_scheduling.json
%   eclipse -b model.ecl -e "run('resource_constrained_project_scheduling_1.dat'), halt"
%
% The data fields, lists indexed from 0 as in the JSON: durations_data[J] is the duration of job J;
% resource_needs_data[J][R] is the amount of resource R that job J needs; resource_capacities_data[R] is the capacity
% of resource R; successors_link_data holds pairs [I, J] meaning that job I must be completed before job J starts.

:- lib(ic).
:- lib(ic_edge_finder).
:- lib(branch_and_bound).

% Output start_time: the start time of each job, from 0.
model(Instance, Vars, [start_time-Starts], min(Makespan)) :-
    memberchk(durations_data-Durations, Instance),
    memberchk(resource_capacities_data-Capacities, Instance),
    memberchk(resource_needs_data-Needs, Instance),
    memberchk(successors_link_data-Links, Instance),
    length(Durations, NumJobs),
    length(Starts, NumJobs),
    total_of(Durations, Horizon),

    % a job starts within the horizon, the sum of all durations
    Starts :: 0..Horizon,
    Makespan :: 0..Horizon,

    % a job starts only after the jobs that must be completed before it
    precedences(Links, Starts, Durations),

    % at no time does the use of a resource exceed its capacity
    length(Capacities, NumResources),
    ( for(R, 1, NumResources), param(Starts, Durations, Needs, Capacities) do
        column_items(Needs, R, Demands),
        nth_item(R, Capacities, Capacity),
        cumulative(Starts, Durations, Demands, Capacity)
    ),

    % the makespan is at least the end of every job
    ( foreach(S, Starts), foreach(D, Durations), param(Makespan) do
        S + D #=< Makespan
    ),

    app(Starts, [Makespan], Vars).

% the jobs I and J of each pair [I, J]: job J starts after job I has finished
precedences([], _, _).
precedences([[I, J] | Links], Starts, Durations) :-
    I1 is I + 1,
    J1 is J + 1,
    nth_item(I1, Starts, SI),
    nth_item(I1, Durations, DI),
    nth_item(J1, Starts, SJ),
    SI + DI #=< SJ,
    precedences(Links, Starts, Durations).

% the amount of resource R (counting from 1) that each job needs
column_items([], _, []).
column_items([Row | Rows], R, [D | Ds]) :-
    nth_item(R, Row, D),
    column_items(Rows, R, Ds).

% the sum of a list of numbers
total_of([], 0).
total_of([X | Xs], S) :-
    total_of(Xs, S0),
    S is X + S0.

% the I-th item of a list, counting from 1
nth_item(1, [X | _], X) :- !.
nth_item(I, [_ | Xs], X) :-
    I > 1,
    I1 is I - 1,
    nth_item(I1, Xs, X).

app([], Ys, Ys).
app([X | Xs], Ys, [X | Zs]) :-
    app(Xs, Ys, Zs).

% the search picks the variable with the fewest candidate values first and tries the lowest value first
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

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

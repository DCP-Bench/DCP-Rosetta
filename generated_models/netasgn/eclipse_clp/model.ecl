% netasgn: an ECLiPSe model from DCP Rosetta.
%
% Consider a project assignment problem. Given a set of people and a set of projects. Each person has a certain number
% of available hours, and each project requires a certain number of hours. The cost per hour of work for a person on a
% project is given, and each person can contribute to a project up to a maximum limit of hours. The problem is to
% decide the number of hours to be assigned from each person to each project, so that the total cost is minimized. The
% total number of hours assigned from each person equals its supply, and the total number of hours assigned to each
% project equals its demand.
%
% Save this file as model.ecl. Download `netasgn.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py netasgn.json
%   eclipse -b model.ecl -e "run('netasgn_1.dat'), halt"
%
% The data fields, lists indexed from 0 as in the JSON: supply[I] is the hours person I has available, demand[J] is the
% hours project J requires, cost[I][J] is the cost per hour of person I on project J, and limit[I][J] is the most hours
% person I can contribute to project J.

:- lib(ic).
:- lib(branch_and_bound).

% Output assign: assign[I][J] is the number of hours assigned from person I to project J.
model(Instance, Vars, [assign-Rows, total_cost-Total], min(Total)) :-
    memberchk(supply-Supply, Instance),
    memberchk(demand-Demand, Instance),
    memberchk(cost-Cost, Instance),
    memberchk(limit-Limit, Instance),
    length(Supply, NumPeople),
    length(Demand, NumProjects),
    length(Rows, NumPeople),
    ( foreach(Row, Rows), param(NumProjects) do length(Row, NumProjects) ),
    flatten_rows(Rows, Vars),

    % the hours from each person to each project are between 0 and the limit of that pair
    ( foreach(Row, Rows), foreach(LimitRow, Limit) do
        bounded_hours(Row, LimitRow)
    ),

    % the total number of hours assigned from each person equals its supply
    ( foreach(Row, Rows), foreach(S, Supply) do
        sum(Row) #= S
    ),

    % the total number of hours assigned to each project equals its demand
    columns_of(Rows, Columns),
    ( foreach(Col, Columns), foreach(D, Demand) do
        sum(Col) #= D
    ),

    % the total cost of the hours assigned, which is to be as small as possible
    ( foreach(Row, Rows), foreach(CostRow, Cost), foreach(Part, Parts) do
        Part #= CostRow * Row
    ),
    Total #= sum(Parts).

% the hours of one person to each project lie between 0 and the limit for that project
bounded_hours([], []).
bounded_hours([X | Xs], [L | Ls]) :-
    X :: 0..L,
    bounded_hours(Xs, Ls).

% the columns of a list of rows: the first column is the list of the first items of all rows, and so on
columns_of([[] | _], []) :- !.
columns_of(Rows, [Col | Cols]) :-
    heads_tails(Rows, Col, Tails),
    columns_of(Tails, Cols).

heads_tails([], [], []).
heads_tails([[H | T] | Rows], [H | Hs], [T | Ts]) :-
    heads_tails(Rows, Hs, Ts).

% the items of the rows as one list, row after row
flatten_rows([], []).
flatten_rows([Row | Rows], Vars) :-
    app(Row, Rest, Vars),
    flatten_rows(Rows, Rest).

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

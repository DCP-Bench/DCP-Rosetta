% appointment_scheduling: an ECLiPSe model from DCP Rosetta.
%
% Schedule 4 people into 4 interview slots according to their free-busy schedules. Each person is free in some slots
% and busy in others. Each person gets exactly one slot in which they are free, and each slot goes to exactly one
% person. X[I][J] is true when person I is assigned to slot J, and false otherwise.
%
% Save this file as model.ecl. Download `appointment_scheduling.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py appointment_scheduling.json
%   eclipse -b model.ecl -e "run('appointment_scheduling_1.dat'), halt"

% Instance fields: m (m[I][J] is 1 when person I is free in slot J, 0 when busy; a list of rows indexed from 0).
:- lib(ic).
:- lib(listut).

model(Instance, Vars, [x-Xs]) :-
    memberchk(m-M, Instance),
    length(M, N),
    length(Xs, N),
    ( foreach(Row, Xs), param(N) do length(Row, N) ),
    concat_rows(Xs, Vars),
    % each assignment is a 0/1 flag
    Vars :: 0..1,
    % a person can only be assigned to a slot in which they are free
    ( foreach(Row, Xs), foreach(FreeRow, M) do
        ( foreach(X, Row), foreach(Free, FreeRow) do
            X #=< Free
        ),
        % each person gets exactly one slot
        sum(Row) #= 1
    ),
    % each slot goes to exactly one person
    ( for(J, 1, N), param(Xs) do
        ( foreach(Row, Xs), foreach(X, Col), param(J) do
            nth1(J, Row, X)
        ),
        sum(Col) #= 1
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

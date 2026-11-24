% car_selection: an ECLiPSe model from DCP Rosetta.
%
% Participants are to be assigned to cars so that the total number of assignments is as large as possible. Each
% participant may be interested in only some of the cars, and a participant is assigned only to a car they are
% interested in. Each participant is assigned to at most one car, and each car is assigned to at most one participant.
%
% Save this file as model.ecl. Download `car_selection.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py car_selection.json
%   eclipse -b model.ecl -e "run('car_selection_1.dat'), halt"
%
% Data fields: possible_assignments is the matrix of interests: entry [i][j] is 1 when participant i is interested in
% car j, 0 otherwise (lists indexed from 0 as in the JSON).
:- lib(ic).
:- lib(listut).
:- lib(branch_and_bound).

% Outputs: assignments (the matrix with entry [i][j] equal to 1 when participant i is assigned to car j).
model(Instance, Vars, [assignments-Rows], max(Total)) :-
    memberchk(possible_assignments-Possible, Instance),
    length(Possible, NRows),
    Possible = [FirstRow | _],
    length(FirstRow, NCols),
    length(Rows, NRows),
    bool_rows(Rows, NCols),
    % a participant is assigned only to a car they are interested in
    within_rows(Rows, Possible),
    % each participant is assigned to at most one car
    ( foreach(Row, Rows) do sum(Row) #=< 1 ),
    % each car is assigned to at most one participant
    columns_of(Rows, Cols),
    ( foreach(Col, Cols) do sum(Col) #=< 1 ),
    % the total number of assignments is to be maximized
    flatten(Rows, Flat),
    Total #= sum(Flat),
    append(Flat, [Total], Vars).

% bool_rows(Rows, N): Rows is a list of N rows, each of N 0/1 variables
bool_rows([], _).
bool_rows([Row | Rows], N) :-
    length(Row, N),
    Row :: 0..1,
    bool_rows(Rows, N).

% within_rows(Rows, Possible): each entry of Rows is at most the matching entry of Possible
within_rows([], []).
within_rows([Row | Rows], [PRow | PRows]) :-
    within(Row, PRow),
    within_rows(Rows, PRows).

within([], []).
within([X | Xs], [P | Ps]) :-
    X #=< P,
    within(Xs, Ps).

% columns_of(Rows, Cols): Cols is the transpose of the matrix Rows
columns_of([[] | _], []) :- !.
columns_of(Rows, [Col | Cols]) :-
    firsts_rests(Rows, Col, Rest),
    columns_of(Rest, Cols).

firsts_rests([], [], []).
firsts_rests([[H | T] | Rs], [H | Hs], [T | Ts]) :-
    firsts_rests(Rs, Hs, Ts).

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

% csplib_067_quasigroup_completion: an ECLiPSe model from DCP Rosetta.
%
% An order N quasigroup is a Latin square of size N: an N x N multiplication table over the symbols 1 to N in which
% every symbol occurs exactly once in every row and every column. Complete a partially filled quasigroup, where 0
% marks an empty cell.
%
% Save this file as model.ecl. Download `csplib_067_quasigroup_completion.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_067_quasigroup_completion.json
%   eclipse -b model.ecl -e "run('csplib_067_quasigroup_completion_1.dat'), halt"
%
% The data fields: N is the order of the quasigroup, start the partially filled table (rows of N entries, 0 for an
% empty cell); lists are indexed from 0 as in the JSON.

:- lib(ic).
:- lib(listut).

% Puzzle[R][C] is the symbol in row R and column C (rows and columns counted from 0 as in the JSON, symbols from 1 to N).
model(Instance, Vars, [puzzle-Rows]) :-
    memberchk('N'-N, Instance),
    memberchk(start-Start, Instance),
    length(Rows, N),
    ( foreach(Row, Rows), param(N) do
        length(Row, N),
        Row :: 1..N
    ),
    flatten(Rows, Vars),

    % a given symbol stays in its cell; a 0 marks an empty cell
    ( foreach(SRow, Start), foreach(Row, Rows) do
        ( foreach(S, SRow), foreach(X, Row) do
            ( S > 0 -> X #= S ; true )
        )
    ),

    % each row contains each symbol exactly once
    ( foreach(Row, Rows) do
        alldifferent(Row)
    ),

    % each column contains each symbol exactly once
    ( for(C, 1, N), param(Rows) do
        column(Rows, C, Col),
        alldifferent(Col)
    ).

% the cells of column C, top to bottom
column(Rows, C, Col) :-
    ( foreach(Row, Rows), foreach(X, Col), param(C) do
        nth1(C, Row, X)
    ).

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

% csplib_054_n_queens: an ECLiPSe model from DCP Rosetta.
%
% Can n queens be placed on an n x n chessboard so that no two queens attack each other? A queen attacks the squares
% on its row, its column and its two diagonals, so no two queens may share a row, a column or a diagonal.
%
% Save this file as model.ecl. Download `csplib_054_n_queens.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_054_n_queens.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_054_n_queens.json
%   eclipse -b model.ecl -e "run('csplib_054_n_queens_1.dat'), halt"
%
% The data field n is the size of the board and the number of queens; lists are indexed from 0 as in the JSON.

:- lib(ic).
:- lib(listut).

% Queens[I] is the column (1-based) of the queen in row I (1-based).
model(Instance, Queens, [queens-Queens]) :-
    memberchk(n-N, Instance),
    length(Queens, N),
    Queens :: 1..N,

    % no two queens share a column
    alldifferent(Queens),

    % no two queens share a diagonal: the sums Queen+Row are all different, and so are the differences Queen-Row
    ( for(I, 1, N), foreach(S, Sums), param(Queens) do
        nth1(I, Queens, Q),
        S #= Q + I
    ),
    ( for(I, 1, N), foreach(D, Diffs), param(Queens) do
        nth1(I, Queens, Q),
        D #= Q - I
    ),
    alldifferent(Sums),
    alldifferent(Diffs).

search_goal(Queens) :-
    search(Queens, 0, first_fail, indomain_min, complete, []).
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

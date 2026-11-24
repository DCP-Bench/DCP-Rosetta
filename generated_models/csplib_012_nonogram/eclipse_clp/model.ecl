% csplib_012_nonogram: an ECLiPSe model from DCP Rosetta.
%
% Nonograms are a puzzle in which the solver shades squares of a grid so that the blocks of consecutive shaded squares
% satisfy the constraints given for each row and each column. A constraint is the sequence of shaded blocks in that
% line: 3,1,2 means a block of 3, then a gap of unspecified size, a block of 1, another gap, and a block of 2.
%
% Save this file as model.ecl. Download `csplib_012_nonogram.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_012_nonogram.json
%   eclipse -b model.ecl -e "run('csplib_012_nonogram_1.dat'), halt"

% Instance fields: rows and cols (the grid size), row_rules (the block sequence of each row, one list per
% row) and col_rules (the same for each column). A block sequence is padded with 0s, which are ignored.
% Output board: board[I][J] is 1 when the square in row I, column J is shaded, 0 otherwise.

:- lib(ic).
:- lib(lists).
:- lib(listut).

model(Instance, Vars, [board-Board]) :-
    memberchk(rows-R, Instance),
    memberchk(cols-C, Instance),
    memberchk(row_rules-RowRules, Instance),
    memberchk(col_rules-ColRules, Instance),
    % one 0/1 variable per square
    length(Board, R),
    ( foreach(Row, Board), param(C) do
        length(Row, C),
        Row :: 0..1
    ),
    % each row: its blocks, in order, are the shaded runs of the row
    ( foreach(Row, Board), foreach(Clue, RowRules), foreach(Starts, RowStarts) do
        line_clue(Row, Clue, Starts)
    ),
    % each column: its blocks, in order, are the shaded runs of the column
    transpose_board(Board, Cols),
    ( foreach(Col, Cols), foreach(Clue, ColRules), foreach(Starts, ColStarts) do
        line_clue(Col, Clue, Starts)
    ),
    flatten(Board, BoardVars),
    flatten(RowStarts, RowStartVars),
    flatten(ColStarts, ColStartVars),
    append(BoardVars, RowStartVars, V1),
    append(V1, ColStartVars, Vars).

% A line of cells whose shaded runs are exactly the blocks of Clue, in order. The start of each block is an auxiliary
% variable (Starts), with one start per block.
line_clue(Cells, Clue, Starts) :-
    nonzero(Clue, Blocks),
    length(Cells, N),
    length(Blocks, K),
    length(Starts, K),
    (   K == 0
    ->  ( foreach(X, Cells) do X #= 0 )
    ;   Starts :: 1..N,
        place(Starts, Blocks, N),
        post_cells(Cells, 1, Starts, Blocks)
    ).

% the blocks are placed from left to right, each one inside the line, with at least one unshaded square between two
% consecutive blocks
place([S], [B], N) :-
    S #=< N - B + 1.
place([S1, S2 | Ss], [B1 | Bs], N) :-
    S1 #=< N - B1 + 1,
    S2 #>= S1 + B1 + 1,
    place([S2 | Ss], Bs, N).

% a square is shaded exactly when it lies inside one of the blocks
post_cells([], _, _, _).
post_cells([X | Xs], J, Starts, Blocks) :-
    cover(Starts, Blocks, J, Ins),
    X #= sum(Ins),
    J1 is J + 1,
    post_cells(Xs, J1, Starts, Blocks).

% In[K] is 1 when square J lies in block K, which starts at S and has length B
cover([], [], _, []).
cover([S | Ss], [B | Bs], J, [In | Ins]) :-
    In #= (S #=< J and S + B #> J),
    cover(Ss, Bs, J, Ins).

% the non-zero entries of a clue, in order
nonzero([], []).
nonzero([X | Xs], Ys) :-
    (   X =:= 0
    ->  Ys = Ys1
    ;   Ys = [X | Ys1]
    ),
    nonzero(Xs, Ys1).

% the columns of the board, from its rows
transpose_board([[] | _], []) :- !.
transpose_board(Rows, [Col | Cols]) :-
    first_column(Rows, Col, Rest),
    transpose_board(Rest, Cols).

first_column([], [], []).
first_column([[H | T] | Rs], [H | Hs], [T | Ts]) :-
    first_column(Rs, Hs, Ts).

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

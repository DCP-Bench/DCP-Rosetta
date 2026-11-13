% minesweeper: an ECLiPSe model from DCP Rosetta.
%
% Minesweeper rules are simple. The board is divided into cells, with mines randomly distributed. To win, you need to
% open all the cells. The number on a cell shows the number of mines adjacent to it. Using this information, you can
% determine cells that are safe, and cells that contain mines. The task is to determine which unopened cells contain
% mines, based on the numerical clues of the opened cells. An opened cell is not a mine, and the number on it is the
% number of mines among the (up to eight) cells next to it.
%
% Save this file as model.ecl. Download `minesweeper.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py minesweeper.json
%   eclipse -b model.ecl -e "run('minesweeper_1.dat'), halt"
%
% The data fields: X is the value that marks an unopened cell in the board; game_data[R][C] is the value of the cell in
% row R and column C of the board, rows and columns counted from 0 as in the JSON: X for an unopened cell, otherwise the
% number on the opened cell. The board has as many rows as game_data has items, and as many columns as each row has
% items, so it need not be square.

:- lib(ic).
:- lib(branch_and_bound).

% Output mines: mines[R][C] is 1 when the cell in row R and column C is a mine, 0 otherwise.
model(Instance, Vars, [mines-Rows]) :-
    memberchk('X'-Unopened, Instance),
    memberchk(game_data-Board, Instance),
    Board = [FirstRow | _],
    length(Board, NumRows),
    length(FirstRow, NumCols),

    % the mines grid has the same shape as the board
    length(Rows, NumRows),
    ( foreach(Row, Rows), param(NumCols) do length(Row, NumCols) ),
    flatten_rows(Rows, Vars),

    % each cell is a mine (1) or not (0)
    Vars :: 0..1,

    % the clues: an opened cell is not a mine, and the number on it is the number of mines next to it
    clue_rows(Board, 1, Rows, NumRows, NumCols, Unopened).

% the clues of the rows of the board, the first row being row R
clue_rows([], _, _, _, _, _).
clue_rows([BoardRow | BoardRows], R, Rows, NumRows, NumCols, Unopened) :-
    clue_cells(BoardRow, 1, R, Rows, NumRows, NumCols, Unopened),
    R1 is R + 1,
    clue_rows(BoardRows, R1, Rows, NumRows, NumCols, Unopened).

% the clues of the cells of one row of the board, the first cell being column C
clue_cells([], _, _, _, _, _, _).
clue_cells([Value | Values], C, R, Rows, NumRows, NumCols, Unopened) :-
    (   Value =:= Unopened
    ->  true
    ;   % an opened cell is not a mine
        grid_cell(Rows, R, C, Mine),
        Mine #= 0,
        % the number on it is the number of mines among the cells next to it
        adjacent_cells(R, C, NumRows, NumCols, Cells),
        cells_vars(Cells, Rows, Adjacent),
        sum(Adjacent) #= Value
    ),
    C1 is C + 1,
    clue_cells(Values, C1, R, Rows, NumRows, NumCols, Unopened).

% the cells next to the cell in row R and column C, that are on the board
adjacent_cells(R, C, NumRows, NumCols, Cells) :-
    adjacent_offsets(Offsets),
    adjacent_on_board(Offsets, R, C, NumRows, NumCols, Cells).

adjacent_offsets([-1-(-1), -1-0, -1-1, 0-(-1), 0-1, 1-(-1), 1-0, 1-1]).

adjacent_on_board([], _, _, _, _, []).
adjacent_on_board([DR-DC | Offsets], R, C, NumRows, NumCols, Cells) :-
    R1 is R + DR,
    C1 is C + DC,
    (   R1 >= 1, R1 =< NumRows, C1 >= 1, C1 =< NumCols
    ->  Cells = [R1-C1 | Rest]
    ;   Cells = Rest
    ),
    adjacent_on_board(Offsets, R, C, NumRows, NumCols, Rest).

% the variables of the listed cells
cells_vars([], _, []).
cells_vars([R-C | Cells], Rows, [V | Vs]) :-
    grid_cell(Rows, R, C, V),
    cells_vars(Cells, Rows, Vs).

% the cell in row R and column C, counting from 1
grid_cell(Rows, R, C, V) :-
    nth_item(R, Rows, Row),
    nth_item(C, Row, V).

% the I-th item of a list, counting from 1
nth_item(1, [X | _], X) :- !.
nth_item(I, [_ | Xs], X) :-
    I > 1,
    I1 is I - 1,
    nth_item(I1, Xs, X).

% the cells of the board as one list, row after row
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

% n_puzzle: an ECLiPSe model from DCP Rosetta.
%
% The N-Puzzle is a classic sliding puzzle: a square grid of tiles numbered 1 upwards, one of which is the empty tile,
% marked 0. Each step moves one tile that is horizontally or vertically next to the empty tile into the empty position.
% Freezing is not allowed: the state of the puzzle must change at each step. Trace the steps from the start board to the
% end board, using exactly N_STEPS boards, the start and the end board included.
%
% Save this file as model.ecl. Download `n_puzzle.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py n_puzzle.json
%   eclipse -b model.ecl -e "run('n_puzzle_1.dat'), halt"
%
% The data fields: N_STEPS is the number of boards in the sequence; puzzle_start and puzzle_end are the start and the
% end board, each as rows of tiles (lists indexed from 0 as in the JSON), with 0 for the empty tile. The board is
% square, so its side is the number of its rows.

:- lib(ic).
:- lib(branch_and_bound).

% Output steps: the N_STEPS boards of the sequence, each one as rows of tiles.
%
% Board t is a list of the tiles of the squares, numbered 1 to NS = Side*Side row by row. Blanks[t] is the square of
% the empty tile on board t.
model(Instance, Vars, [steps-Steps]) :-
    memberchk('N_STEPS'-K, Instance),
    memberchk(puzzle_start-StartRows, Instance),
    memberchk(puzzle_end-EndRows, Instance),
    length(StartRows, Side),
    NS is Side * Side,
    flatten_rows(StartRows, StartTiles),
    flatten_rows(EndRows, EndTiles),

    % the row and the column of each square, squares numbered from 1
    square_positions(1, NS, Side, Rows, Cols),

    % each board holds the tiles 0 to NS-1, all different
    length(States, K),
    ( foreach(State, States), param(NS) do
        length(State, NS),
        State :: 0..NS-1,
        alldifferent(State)
    ),

    % the first board is the start board and the last board is the end board
    States = [FirstState | _],
    FirstState = StartTiles,
    last_item(States, LastState),
    LastState = EndTiles,

    % the square of the empty tile on each board
    length(Blanks, K),
    Blanks :: 1..NS,
    empty_flags_all(States, Blanks, FlagsAll),

    % each step moves one tile into the empty square: the empty square moves to a square next to it
    moves(States, Blanks, FlagsAll, Rows, Cols),

    % the output: each board as rows of Side tiles
    ( foreach(State, States), foreach(Board, Steps), param(Side) do
        split_rows(State, Side, Board)
    ),

    % the search picks the empty squares first, then the tiles follow from them
    app(Blanks, FlatStates, Vars),
    concat_all(States, FlatStates).

% the row and the column of each square Q, counting from 1, on a board of the given side
square_positions(Q, NS, Side, [R | Rs], [C | Cs]) :-
    Q =< NS,
    !,
    R is (Q - 1) // Side,
    C is (Q - 1) mod Side,
    Q1 is Q + 1,
    square_positions(Q1, NS, Side, Rs, Cs).
square_positions(_, _, _, [], []).

% for each board, a 0/1 flag per square: 1 when the empty tile is on that square
empty_flags_all([], [], []).
empty_flags_all([State | States], [Blank | Blanks], [Flags | FlagsAll]) :-
    empty_flags(State, Blank, 1, Flags),
    empty_flags_all(States, Blanks, FlagsAll).

% the flag of each square: 1 exactly when the square holds the empty tile (0) and is the square of the empty tile
empty_flags([], _, _, []).
empty_flags([Tile | Tiles], Blank, Q, [Flag | Flags]) :-
    Flag #= (Tile #= 0),
    Flag #= (Blank #= Q),
    Q1 is Q + 1,
    empty_flags(Tiles, Blank, Q1, Flags).

% each board goes to the next one by one slide
moves([_], [_], [_], _, _).
moves([State, Next | States], [Blank, NextBlank | Blanks], [Flags, NextFlags | FlagsAll], Rows, Cols) :-
    % the empty square moves to a square next to it, horizontally or vertically
    element(Blank, Rows, R1), element(Blank, Cols, C1),
    element(NextBlank, Rows, R2), element(NextBlank, Cols, C2),
    DR #= abs(R1 - R2),
    DC #= abs(C1 - C2),
    DR + DC #= 1,
    % the tile that moves into the empty square is the tile on the square it moves to
    element(NextBlank, State, Moved),
    slide(Next, State, Flags, NextFlags, Moved),
    moves([Next | States], [NextBlank | Blanks], [NextFlags | FlagsAll], Rows, Cols).

% the tiles of the next board: the moved tile on the square the empty tile leaves, the empty tile on the square it
% moves to, and the other tiles unchanged
slide([], [], [], [], _).
slide([NextTile | NextTiles], [Tile | Tiles], [Flag | Flags], [NextFlag | NextFlags], Moved) :-
    NextTile #= Flag * Moved + (1 - Flag - NextFlag) * Tile,
    slide(NextTiles, Tiles, Flags, NextFlags, Moved).

% the last item of a nonempty list
last_item([X], X) :- !.
last_item([_ | Xs], X) :-
    last_item(Xs, X).

% the items of the rows as one list, row after row
flatten_rows([], []).
flatten_rows([Row | Rows], Vars) :-
    app(Row, Rest, Vars),
    flatten_rows(Rows, Rest).

% all the boards as one list of tiles
concat_all([], []).
concat_all([Board | Boards], Vars) :-
    app(Board, Rest, Vars),
    concat_all(Boards, Rest).

% the list split into rows of Side items each
split_rows([], _, []).
split_rows(Items, Side, [Row | Rows]) :-
    take(Side, Items, Row, Rest),
    split_rows(Rest, Side, Rows).

take(0, Rest, [], Rest) :- !.
take(K, [X | Xs], [X | Ys], Rest) :-
    K1 is K - 1,
    take(K1, Xs, Ys, Rest).

app([], Ys, Ys).
app([X | Xs], Ys, [X | Zs]) :-
    app(Xs, Ys, Zs).

% the search labels the empty squares in order, then the tiles
search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_min, complete, []).

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

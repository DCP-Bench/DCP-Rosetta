% minesweeper: a SWI-Prolog model from DCP Rosetta.
%
% Minesweeper: the board is divided into cells, with mines distributed among them. The number on an opened cell shows
% the number of mines adjacent to it (among its up to eight neighbours). From the numbers revealed on the board,
% determine which of the unopened cells contain a mine, and which do not.
%
% Save this file as model.pl. Download `minesweeper.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('minesweeper.json')" -t halt model.pl
%
% Data fields: X (the value that marks a cell that is not opened), game_data (the board, a list of rows; a cell
% holds either X or the number of mines adjacent to it, rows and columns indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).
:- use_module(library(http/json)).

model(Instance, Flat, [mines-Rows]) :-
    Unopened = Instance.'X',
    Game = Instance.game_data,
    length(Game, NRows),
    Game = [FirstRow|_],
    length(FirstRow, NCols),
    % Rows[R][C] is 1 when cell (R, C) holds a mine, 0 when it is safe; rows are counted from 1 here
    length(Rows, NRows),
    maplist({NCols}/[Row]>>(length(Row, NCols), Row ins 0..1), Rows),
    append(Rows, Flat),
    % the opened cells, with their numbers
    findall(clue(R, C, Number),
            (nth1(R, Game, GameRow), nth1(C, GameRow, Number), Number \== Unopened),
            Clues),
    maplist(clue_holds(Rows), Clues).

% clue_holds(+Rows, +Clue): an opened cell is safe, and its number is the count of mines among its neighbours
clue_holds(Rows, clue(R, C, Number)) :-
    % an opened cell is not a mine
    cell(Rows, R, C, 0),
    length(Rows, NRows),
    Rows = [FirstRow|_],
    length(FirstRow, NCols),
    findall(A-B, neighbour(NRows, NCols, R, C, A, B), Around),
    maplist(cell_mine(Rows), Around, Mines),
    sum(Mines, #=, Number).

% neighbour(+NRows, +NCols, +R, +C, -A, -B): (A, B) is a cell next to (R, C) on a board of NRows by NCols
neighbour(NRows, NCols, R, C, A, B) :-
    between(-1, 1, DA),
    between(-1, 1, DB),
    \+ (DA =:= 0, DB =:= 0),
    A is R + DA, B is C + DB,
    A >= 1, A =< NRows, B >= 1, B =< NCols.

cell_mine(Rows, A-B, Mine) :-
    cell(Rows, A, B, Mine).

% cell(+Rows, +R, +C, ?Value): the cell in row R and column C (both counted from 1)
cell(Rows, R, C, Value) :-
    nth1(R, Rows, Row),
    nth1(C, Row, Value).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).

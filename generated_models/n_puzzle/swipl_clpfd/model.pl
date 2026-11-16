% n_puzzle: a SWI-Prolog model from DCP Rosetta.
%
% The N-Puzzle is a classic sliding puzzle: a grid holds n+1 tiles, one of which is empty (0), and the goal is to move
% the tiles into their correct positions. Trace a sequence of N_STEPS boards, from the start state to the end state
% (both included). Each step moves one tile that is horizontally or vertically next to the empty square into the empty
% square, and the state of the puzzle must change at each step.
%
% Save this file as model.pl. Download `n_puzzle.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/n_puzzle.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('n_puzzle.json')" -t halt model.pl
%
% Data fields: N_STEPS (the number of boards in the sequence, start and end included), puzzle_start and puzzle_end
% (the start and end boards, as lists of rows, 0 being the empty square; rows and columns indexed from 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).
:- use_module(library(http/json)).

model(Instance, Blanks-Flats, [steps-Steps]) :-
    NSteps = Instance.'N_STEPS',
    StartRows = Instance.puzzle_start,
    EndRows = Instance.puzzle_end,
    length(StartRows, Dim),
    Squares is Dim * Dim,
    Last is Squares - 1,
    % Flats[T] is the board at step T, its squares in row-major order from 0
    length(Flats, NSteps),
    maplist(board(Squares, Last), Flats),
    % the first board is the start state and the last one the end state
    append(StartRows, StartFlat),
    Flats = [StartFlat|_],
    append(EndRows, EndFlat),
    last(Flats, EndFlat),
    % Blanks[T] is the square holding the empty tile at step T
    length(Blanks, NSteps),
    Blanks ins 0..Last,
    maplist(blank_at, Blanks, Flats),
    % each step slides a tile from a square next to the empty square into it
    neighbours(Dim, Neighbours),
    chain(Flats, Blanks, Neighbours),
    % Steps[T] is the board at step T as a list of rows
    length(Steps, NSteps),
    maplist(board_rows(Dim), Steps, Flats).

% board(+Squares, +Last, -Flat): a board is a permutation of the tiles 0..Last
board(Squares, Last, Flat) :-
    length(Flat, Squares),
    Flat ins 0..Last,
    all_distinct(Flat).

% blank_at(+Blank, +Flat): the empty tile is on square Blank
blank_at(Blank, Flat) :-
    Index #= Blank + 1,
    element(Index, Flat, 0).

% neighbours(+Dim, -Pairs): the pairs [From, To] of squares sharing a side on a Dim by Dim board
neighbours(Dim, Pairs) :-
    Max is Dim - 1,
    findall([From, To],
            (   between(0, Max, R), between(0, Max, C), From is R * Dim + C,
                member([DR, DC], [[1, 0], [-1, 0], [0, 1], [0, -1]]),
                R2 is R + DR, C2 is C + DC,
                between(0, Max, R2), between(0, Max, C2),
                To is R2 * Dim + C2
            ),
            Pairs).

% chain(+Flats, +Blanks, +Neighbours): each board follows from the one before by one slide
chain([_], [_], _).
chain([Before, After|Boards], [From, To|Blanks], Neighbours) :-
    % the empty square moves to a neighbouring square
    tuples_in([[From, To]], Neighbours),
    % the tile on the square the empty tile moves to slides into the square it leaves
    Into #= To + 1,
    element(Into, Before, Moved),
    OutOf #= From + 1,
    element(OutOf, After, Moved),
    % every other square keeps its tile
    length(Before, Squares),
    Last is Squares - 1,
    numlist(0, Last, Indices),
    maplist(keeps_tile(Before, After, From, To), Indices),
    chain([After|Boards], [To|Blanks], Neighbours).

% keeps_tile(+Before, +After, +From, +To, +Square): a square other than the two the empty tile leaves or enters
% holds the same tile in both boards
keeps_tile(Before, After, From, To, Square) :-
    nth0(Square, Before, B),
    nth0(Square, After, A),
    (Square #\= From #/\ Square #\= To) #==> (A #= B).

% board_rows(+Dim, -Rows, +Flat): the board as Dim rows of Dim tiles
board_rows(Dim, Rows, Flat) :-
    length(Rows, Dim),
    maplist(row_of_length(Dim), Rows),
    append(Rows, Flat).

row_of_length(Dim, Row) :-
    length(Row, Dim).

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

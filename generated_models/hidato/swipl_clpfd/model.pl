% hidato: a SWI-Prolog model from DCP Rosetta.
%
% Hidato puzzles start semi-filled with numbered tiles. Connect the numbers together to win: consecutive numbers
% must touch horizontally, vertically or diagonally, and the numbers must be in increasing order. Fill in the empty
% cells, marked 0 in the given puzzle, with numbers so that the grid holds each number from 1 to the number of cells
% exactly once.
%
% Save this file as model.pl. Download `hidato.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('hidato.json')" -t halt model.pl
%
% Data fields: puzzle (the grid as a list of rows, indexed from 0; a 0 marks an empty cell, any other value is a
% number given in the puzzle).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).
:- use_module(library(http/json)).

model(Instance, Vars, [x-Rows]) :-
    Puzzle = Instance.puzzle,
    length(Puzzle, Height),
    Puzzle = [FirstRow|_],
    length(FirstRow, Width),
    Count is Height * Width,               % the number of cells, which is also the largest number
    % Rows[R][C] is the number in row R and column C of the grid
    length(Rows, Height),
    maplist({Width}/[Row]>>length(Row, Width), Rows),
    append(Rows, Cells),
    % each number from 1 to the number of cells is used exactly once
    Cells ins 1..Count,
    all_distinct(Cells),
    % the numbers given in the puzzle keep their places
    maplist(keep_givens, Puzzle, Rows),
    % Positions[K] is the position in the flattened grid (counted from 1) of the number K
    numlist(1, Count, Numbers),
    length(Positions, Count),
    Positions ins 1..Count,
    maplist(position_of(Cells), Numbers, Positions),
    % consecutive numbers touch, horizontally, vertically or diagonally
    touching_chain(Width, Positions),
    Vars = [Rows, Positions].

% keep_givens(+GivenRow, ?Row): the cells of Row with a given number (not 0) hold that number
keep_givens(GivenRow, Row) :-
    maplist(keep_given, GivenRow, Row).

keep_given(Given, Cell) :-
    (   Given =:= 0
    ->  true
    ;   Cell #= Given
    ).

% position_of(+Cells, +Number, -Position): the flattened position of Number is the one holding it
position_of(Cells, Number, Position) :-
    element(Position, Cells, Number).

% touching_chain(+Width, +Positions): each position touches the next one, in row and column terms
touching_chain(_, [_]).
touching_chain(Width, [P, Q|Rest]) :-
    touch(Width, P, Q),
    touching_chain(Width, [Q|Rest]).

% touch(+Width, +P, +Q): the cells at positions P and Q differ by at most one row and one column
touch(Width, P, Q) :-
    RowP #= (P - 1) // Width,
    ColP #= (P - 1) mod Width,
    RowQ #= (Q - 1) // Width,
    ColQ #= (Q - 1) mod Width,
    abs(RowP - RowQ) #=< 1,
    abs(ColP - ColQ) #=< 1.

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

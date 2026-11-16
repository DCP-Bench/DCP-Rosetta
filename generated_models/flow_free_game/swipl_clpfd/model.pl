% flow_free_game: a SWI-Prolog model from DCP Rosetta.
%
% Connect matching colours with pipes to create a flow: pair all the colours and cover the entire 5 by 5 board, with
% pipes that do not cross or overlap. Cells are connected horizontally and vertically: a numbered cell has exactly
% one neighbour of its own colour, and a filled cell has exactly two. Each colour is an integer from 1 to 5, and
% every empty cell is filled with one of them. The numbered cells are given by the data, and 0 marks an empty cell.
%
% Save this file as model.pl. Download `flow_free_game.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('flow_free_game.json')" -t halt model.pl
%
% Data fields: board (the grid of cells, one list per row, indexed from 0; 0 for an empty cell, otherwise the
% colour of a numbered cell).
:- use_module(library(clpfd)).

model(Instance, Vars, ['B'-Rows]) :-
    Board = Instance.board,
    length(Board, N),                      % the board is N by N
    Last is N - 1,
    append(Board, Given),
    max_list(Given, K),                    % the colours are 1 to K, K being the largest value on the board
    length(Rows, N),
    maplist(row_of_length(N), Rows),
    append(Rows, Vars),
    Vars ins 1..K,
    findall(I-J, (between(0, Last, I), between(0, Last, J)), Cells),
    maplist(cell_rule(Rows, Board, Last), Cells).

row_of_length(N, Row) :-
    length(Row, N).

% a numbered cell has one neighbour of its colour, an empty cell (filled later) has two
cell_rule(Rows, Board, Last, I-J) :-
    nth0(I, Rows, Row), nth0(J, Row, Colour),
    nth0(I, Board, BoardRow), nth0(J, BoardRow, Given),
    (   Given =:= 0
    ->  Degree = 2
    ;   Colour #= Given, Degree = 1
    ),
    findall(I2-J2, adjacent(Last, I, J, I2, J2), Ns),
    maplist(same_colour(Rows, Colour), Ns, Same),
    sum(Same, #=, Degree).

adjacent(Last, I, J, I2, J2) :-
    member(DI-DJ, [-1-0, 1-0, 0-(-1), 0-1]),
    I2 is I + DI,
    J2 is J + DJ,
    I2 >= 0, I2 =< Last,
    J2 >= 0, J2 =< Last.

% 1 when the neighbour at I-J has the same colour
same_colour(Rows, Colour, I-J, Same) :-
    nth0(I, Rows, Row), nth0(J, Row, Other),
    Same #<==> (Colour #= Other).

:- use_module(library(http/json)).

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

% session1_magic_square: a SWI-Prolog model from DCP Rosetta.
%
% A magic square is an n x n grid (n is not 2) such that each cell contains a different integer from 1 to n^2 and the
% sum of the integers in each row, column and diagonal is equal. Find a magic square for a given size n, knowing that
% the sum of the integers of each row, column and diagonal has to be n(n^2 + 1)/2.
%
% Save this file as model.pl. Download `session1_magic_square.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_magic_square.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('session1_magic_square.json')" -t halt model.pl
%
% Data fields: n (the size of the square, a side of n cells).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [square-Rows]) :-
    N = Instance.n,
    Cells is N * N,
    Magic is N * (N * N + 1) // 2,         % the common sum of a row, a column or a diagonal
    % Rows[I] is row I of the square, with N cells
    length(Rows, N),
    maplist({N}/[Row]>>length(Row, N), Rows),
    append(Rows, Vars),
    % each cell holds a different integer from 1 to n^2
    Vars ins 1..Cells,
    all_distinct(Vars),
    % every row sums to the magic sum
    maplist({Magic}/[Row]>>sum(Row, #=, Magic), Rows),
    % every column sums to the magic sum
    transpose(Rows, Columns),
    maplist({Magic}/[Column]>>sum(Column, #=, Magic), Columns),
    % the falling diagonal (top-left to bottom-right) sums to the magic sum
    numlist(1, N, Positions),
    maplist({Rows}/[I, Cell]>>(nth1(I, Rows, Row), nth1(I, Row, Cell)), Positions, Falling),
    sum(Falling, #=, Magic),
    % the rising diagonal (top-right to bottom-left) sums to the magic sum
    maplist({Rows, N}/[I, Cell]>>(J is N + 1 - I, nth1(I, Rows, Row), nth1(J, Row, Cell)), Positions, Rising),
    sum(Rising, #=, Magic).

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

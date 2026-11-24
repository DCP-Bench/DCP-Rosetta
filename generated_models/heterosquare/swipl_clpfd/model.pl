% heterosquare: a SWI-Prolog model from DCP Rosetta.
%
% A heterosquare of order n is an n by n square whose elements are distinct integers from 1 to n^2 such that the
% sums of the rows, the columns and the two diagonals are all different from each other.
%
% Save this file as model.pl. Download `heterosquare.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/heterosquare.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('heterosquare.json')" -t halt model.pl
%
% Data fields: n (the order of the square, its side length).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).
:- use_module(library(lists)).
:- use_module(library(http/json)).

model(Instance, Vars, [x-Rows]) :-
    N = Instance.n,
    Size is N * N,
    % Rows[R][C] is the element in row R and column C of the square
    length(Rows, N),
    maplist({N}/[Row]>>length(Row, N), Rows),
    append(Rows, Cells),
    % the elements are distinct integers from 1 to n^2
    Cells ins 1..Size,
    all_distinct(Cells),
    % the sums of the rows are all different from each other, as are the sums of the columns
    % and the sums of the two diagonals, and all these sums are different from one another
    maplist(sum_of, Rows, RowSums),
    transpose(Rows, Columns),
    maplist(sum_of, Columns, ColumnSums),
    numlist(1, N, Indexes),
    maplist(diagonal_element(Rows), Indexes, Diagonal),
    maplist(anti_diagonal_element(N, Rows), Indexes, AntiDiagonal),
    sum_of(Diagonal, DiagonalSum),
    sum_of(AntiDiagonal, AntiDiagonalSum),
    append([RowSums, ColumnSums, [DiagonalSum, AntiDiagonalSum]], Sums),
    all_distinct(Sums),
    Vars = Rows.

% sum_of(+List, -Sum): Sum is the total of the list
sum_of(List, Sum) :-
    sum(List, #=, Sum).

% diagonal_element(+Rows, +R, -Cell): Cell is the element of row R on the main diagonal
diagonal_element(Rows, R, Cell) :-
    nth1(R, Rows, Row),
    nth1(R, Row, Cell).

% anti_diagonal_element(+N, +Rows, +R, -Cell): Cell is the element of row R on the other diagonal, column N+1-R
anti_diagonal_element(N, Rows, R, Cell) :-
    Col is N + 1 - R,
    nth1(R, Rows, Row),
    nth1(Col, Row, Cell).

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

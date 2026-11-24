% kenken: a SWI-Prolog model from DCP Rosetta.
%
% KenKen: fill an n by n grid with the digits 1 to n so that each row and each column holds every digit exactly
% once, and each bold-outlined cage of cells achieves its result with one mathematical operation (addition,
% subtraction, multiplication or division). Digits may repeat within a cage. The operations are not given: a cage of
% one cell holds its result, a cage of two cells may use any of the four operations (a division must be exact), and
% a larger cage uses either addition or multiplication.
%
% Save this file as model.pl. Download `kenken.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('kenken.json')" -t halt model.pl
%
% Data fields: n (the size of the grid), problem (the cages, each a list [Result, Cells], where Cells lists the cells
% of the cage as [Row, Column], counted from 1).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).
:- use_module(library(http/json)).

model(Instance, Vars, [x-Rows]) :-
    N = Instance.n,                        % the grid is N by N
    Cages = Instance.problem,
    % Rows[R][C] is the digit in row R and column C, counted from 1
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 1..N), Rows),
    % each row contains exactly one of each digit
    maplist(all_distinct, Rows),
    % each column contains exactly one of each digit
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),
    % each cage achieves its result with its operation
    maplist(cage_holds(Rows), Cages),
    append(Rows, Vars).

% the digits in the cells of a cage, read from the grid
cage_holds(Rows, [Result, Cells]) :-
    maplist(cell_digit(Rows), Cells, Digits),
    cage(Digits, Result).

cell_digit(Rows, [R, C], Digit) :-
    nth1(R, Rows, Row),
    nth1(C, Row, Digit).

% cage(+Digits, +Result): the digits of the cage reach its result
cage([D], Result) :- !,
    % a cage of one cell holds its result
    D #= Result.
cage([A, B], Result) :- !,
    % a cage of two cells reaches its result by a sum, a difference, a product or an exact quotient
    (A + B #= Result) #\/ (A - B #= Result) #\/ (B - A #= Result) #\/ (A * B #= Result)
    #\/ (A * Result #= B) #\/ (B * Result #= A).
cage(Digits, Result) :-
    % a larger cage reaches its result by its sum or its product
    sum(Digits, #=, Sum),
    foldl([D, P0, P]>>(P #= P0 * D), Digits, 1, Product),
    (Sum #= Result) #\/ (Product #= Result).

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

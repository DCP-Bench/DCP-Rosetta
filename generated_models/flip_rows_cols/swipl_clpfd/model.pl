% flip_rows_cols: a SWI-Prolog model from DCP Rosetta.
%
% Given an array of positive and negative numbers, you may flip the sign of entire rows and columns, as many of them
% as you like. The goal is to make every row and every column sum to a positive number (or zero), and among those
% sign choices to find one whose overall sum is as small as possible. Give the signs of the rows and of the columns,
% as lists of -1 and 1, depending on whether each row or column is kept (1) or flipped (-1).
%
% Save this file as model.pl. Download `flip_rows_cols.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/flip_rows_cols.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('flip_rows_cols.json')" -t halt model.pl
%
% Data fields: input_matrix (the array, one list per row, indexed from 0).
:- use_module(library(clpfd)).

% the column flips are labelled first: with them fixed, the row flips follow by propagation
labeling_options([leftmost]).

model(Instance, Vars, [col_signs-ColSigns, row_signs-RowSigns], min(Total)) :-
    Matrix = Instance.input_matrix,
    length(Matrix, NR),
    Matrix = [FirstRow|_],
    length(FirstRow, NC),
    length(RowFlips, NR), RowFlips ins 0..1,   % 1 when the row is flipped
    length(ColFlips, NC), ColFlips ins 0..1,   % 1 when the column is flipped
    maplist(sign_of, RowFlips, RowSigns),
    maplist(sign_of, ColFlips, ColSigns),
    % a cell changes sign exactly when its row and its column are flipped differently
    maplist(negated_row(ColFlips), RowFlips, Negated),
    % every row sums to a non-negative number after the flips
    maplist(sum_nonneg, Matrix, Negated),
    % every column sums to a non-negative number after the flips
    transpose(Matrix, Columns),
    transpose(Negated, NegatedColumns),
    maplist(sum_nonneg, Columns, NegatedColumns),
    % the overall sum after the flips, to be minimised
    append(Matrix, Flat),
    sum_list(Flat, AllSum),
    twice(Flat, Doubled),
    append(Negated, NegFlat),
    scalar_product(Doubled, NegFlat, #=, Twice),
    Total #= AllSum - Twice,
    Vars = [ColFlips, RowFlips, RowSigns, ColSigns, NegFlat, Total].

sign_of(Flip, Sign) :-
    Sign #= 1 - 2*Flip.

negated_row(ColFlips, RowFlip, Negated) :-
    maplist(differs(RowFlip), ColFlips, Negated).

differs(R, C, N) :-
    N #<==> (R #\= C).

sum_nonneg(Row, NegatedRow) :-
    sum_list(Row, Total),
    twice(Row, Doubled),
    scalar_product(Doubled, NegatedRow, #=<, Total).

twice(As, Ds) :-
    maplist(double, As, Ds).

double(A, D) :-
    D is 2*A.

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

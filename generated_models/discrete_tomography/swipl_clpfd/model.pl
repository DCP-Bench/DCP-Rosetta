% discrete_tomography: a SWI-Prolog model from DCP Rosetta.
%
% This is a little tomography problem, taken from an old issue of Scientific American. A matrix which contains zeroes
% and ones gets x-rayed vertically and horizontally, giving the total number of ones in each row and column. The
% problem is to reconstruct the contents of the matrix from this information.
%
% Save this file as model.pl. Download `discrete_tomography.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/discrete_tomography.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('discrete_tomography.json')" -t halt model.pl
%
% Data fields: row_sums (the number of ones in each row of the matrix), col_sums (the number of ones in each column),
% lists indexed from 0.
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

model(Instance, Vars, [matrix-Rows]) :-
    RowSums = Instance.row_sums,       % the number of ones wanted in each row
    ColSums = Instance.col_sums,       % the number of ones wanted in each column
    length(RowSums, NR),               % one matrix row per row sum
    length(ColSums, NC),               % one matrix column per column sum
    length(Rows, NR),
    maplist({NC}/[Row]>>(length(Row, NC), Row ins 0..1), Rows),
    append(Rows, Vars),                % every cell is a 0/1 variable
    % each row contains as many ones as its row sum
    maplist([Row, Sum]>>sum(Row, #=, Sum), Rows, RowSums),
    % each column contains as many ones as its column sum
    transpose(Rows, Columns),
    maplist([Column, Sum]>>sum(Column, #=, Sum), Columns, ColSums).

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

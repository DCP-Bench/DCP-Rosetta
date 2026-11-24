% sudoku: a SWI-Prolog model from DCP Rosetta.
%
% The goal of Sudoku is to fill a 9x9 grid with numbers so that each row, column and 3x3 section contains all the
% digits between 1 and 9. The input is a grid with some cells filled with numbers and some empty.
%
% Save this file as model.pl. Download `sudoku.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('sudoku.json')" -t halt model.pl
%
% Data fields: input_grid (the 9 rows of the given grid, each a list of 9 numbers indexed from 0, where 0 is an
% empty cell).
:- use_module(library(clpfd)).

model(Instance, Cells, [grid-Rows]) :-
    Given = Instance.input_grid,
    Rows = [R1, R2, R3, R4, R5, R6, R7, R8, R9],
    maplist(nine_cells, Rows),
    append(Rows, Cells),
    Cells ins 1..9,
    % each row contains the digits 1 to 9 once
    maplist(all_distinct, Rows),
    % each column contains the digits 1 to 9 once
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),
    % each 3x3 section contains the digits 1 to 9 once
    sudoku_blocks(R1, R2, R3),
    sudoku_blocks(R4, R5, R6),
    sudoku_blocks(R7, R8, R9),
    % the filled cells keep their given digits
    maplist(maplist(given_cell), Given, Rows).

nine_cells(Row) :- length(Row, 9).

sudoku_blocks([], [], []).
sudoku_blocks([N1, N2, N3|Ns1], [N4, N5, N6|Ns2], [N7, N8, N9|Ns3]) :-
    all_distinct([N1, N2, N3, N4, N5, N6, N7, N8, N9]),
    sudoku_blocks(Ns1, Ns2, Ns3).

given_cell(Given, Cell) :-
    (   Given =:= 0 -> true ; Cell #= Given ).

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

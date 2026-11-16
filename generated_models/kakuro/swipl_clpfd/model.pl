% kakuro: a SWI-Prolog model from DCP Rosetta.
%
% The object of the puzzle is to insert a digit from 1 to 9 inclusive into each white cell such that the sum of the
% numbers in each entry matches the clue associated with it and no digit is duplicated in any entry. Each clue must
% have at least two numbers that add up to it.
%
% Save this file as model.pl. Download `kakuro.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/kakuro.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('kakuro.json')" -t halt model.pl
%
% Data fields: n (the side of the grid, which is n by n), problem (the entries, indexed from 0; each entry is
% [clue, [row, col], [row, col], ...]: its clue, then the cells of the entry, rows and columns counted from 1), and
% blanks (the [row, col] cells, counted from 1, that are black rather than white; they hold 0).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(http/json)).

model(Instance, Vars, [x-Rows]) :-
    N = Instance.n,
    Entries = Instance.problem,
    Blanks = Instance.blanks,
    % Rows[R][C] is the digit in row R and column C of the grid, 0 for a black cell
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 0..9), Rows),
    Vars = Rows,
    % the black cells hold 0
    maplist(black_cell(Rows), Blanks),
    % each entry of the grid
    maplist(entry_constraints(Rows), Entries).

% black_cell(+Rows, +Position): the black cell at Position [Row, Col] holds 0
black_cell(Rows, [R, C]) :-
    cell(Rows, R, C, 0).

% entry_constraints(+Rows, +Entry): the white cells of the entry hold digits from 1 to 9 that add up to its clue
% and no digit is repeated within the entry
entry_constraints(Rows, [Clue|Positions]) :-
    maplist(cell_of(Rows), Positions, Digits),
    % the cells of an entry are white, so each holds a digit from 1 to 9
    Digits ins 1..9,
    % the digits of the entry add up to its clue
    sum(Digits, #=, Clue),
    % no digit is repeated within the entry
    all_distinct(Digits).

% cell_of(+Rows, +Position, -Digit): the digit in the cell at Position [Row, Col]
cell_of(Rows, [R, C], Digit) :-
    cell(Rows, R, C, Digit).

% cell(+Rows, +R, +C, ?Digit): Digit is the entry in row R and column C, counting from 1
cell(Rows, R, C, Digit) :-
    nth1(R, Rows, Row),
    nth1(C, Row, Digit).

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

% futoshiki: a SWI-Prolog model from DCP Rosetta.
%
% The futoshiki puzzle is played on a square grid, such as 5 by 5. Place the digits 1 to N (N being the size of the
% grid) so that each row and each column contains each digit exactly once. Some digits are given at the start, and
% some neighbouring squares are related by inequality signs, so that one must be higher or lower than its neighbour;
% these must be honoured as the grid is filled out. Give the completed grid as a list of lists of integers.
%
% Save this file as model.pl. Download `futoshiki.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/futoshiki.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('futoshiki.json')" -t halt model.pl
%
% Data fields: values (the grid of given digits, one list per row, indexed from 0; 0 for an empty square; its size
% gives N), and lt (one list per inequality, [R1, C1, R2, C2] with 1-based row and column numbers, meaning that the
% square in row R1 and column C1 is less than the square in row R2 and column C2).
:- use_module(library(clpfd)).

model(Instance, Vars, [grid-Rows]) :-
    Given = Instance.values,
    Less = Instance.lt,
    length(Given, N),
    length(Rows, N),
    maplist(row_of(N), Rows),
    append(Rows, Vars),
    Top is N - 1,
    % each square holds a digit from 1 to N
    Vars ins 1..N,
    % each row and each column holds each digit once
    maplist(all_distinct, Rows),
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),
    % the given digits stay where they are
    findall(I-J, (between(0, Top, I), between(0, Top, J)), Cells),
    maplist(given_digit(Rows, Given), Cells),
    % the inequalities between neighbouring squares hold
    maplist(less_than(Rows), Less).

row_of(N, Row) :-
    length(Row, N).

square(Rows, I, J, Square) :-
    nth0(I, Rows, Row),
    nth0(J, Row, Square).

given_digit(Rows, Given, I-J) :-
    nth0(I, Given, GivenRow),
    nth0(J, GivenRow, Digit),
    (   Digit =:= 0
    ->  true
    ;   square(Rows, I, J, Square),
        Square #= Digit
    ).

less_than(Rows, [R1, C1, R2, C2]) :-
    I1 is R1 - 1, J1 is C1 - 1,
    I2 is R2 - 1, J2 is C2 - 1,
    square(Rows, I1, J1, A),
    square(Rows, I2, J2, B),
    A #< B.

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

% csplib_057_killer_sudoku: a SWI-Prolog model from DCP Rosetta.
%
% Killer sudoku (also killer su doku, sumdoku, sum doku, addoku, or samunamupure) is a puzzle that combines elements
% of sudoku and kakuro. The objective is to fill the grid with numbers from 1 to 9 in a way that the following
% conditions are met: each row, column and nonet contains each number exactly once; the sum of all numbers in a cage
% must match the small number printed in its corner; and no number appears more than once in a cage.
%
% Save this file as model.pl. Download `csplib_057_killer_sudoku.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_057_killer_sudoku.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_057_killer_sudoku.json')" -t halt model.pl
%
% Data fields: n (the side of the grid), problem (the cages: a list of [Target, Cells] pairs, where Target is the sum
% of the cage and Cells lists the [Row, Column] of each cell of the cage, counted from 1).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).
:- use_module(library(lists)).

model(Instance, Rows, [x-Rows]) :-
    N = Instance.n,
    Cages = Instance.problem,
    Box is truncate(sqrt(N)),           % the side of a box (a nonet for N = 9)
    Last is Box - 1,
    % Rows[R][C] is the digit in row R and column C, counted from 1
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 1..N), Rows),
    % each row holds every digit once
    maplist(all_distinct, Rows),
    % each column holds every digit once
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),
    % each box holds every digit once
    findall(BR-BC, (between(0, Last, BR), between(0, Last, BC)), Boxes),
    maplist({Rows, Box, N}/[BR-BC]>>(
                findall([R, C], (between(1, N, R), between(1, N, C),
                                 (R - 1) // Box =:= BR, (C - 1) // Box =:= BC), Positions),
                cells_at(Rows, Positions, Cells),
                all_distinct(Cells)), Boxes),
    % each cage adds up to its target and holds no digit twice
    maplist({Rows}/[[Target, Positions]]>>(
                cells_at(Rows, Positions, Cage),
                sum(Cage, #=, Target),
                all_distinct(Cage)), Cages).

% the digits in the cells at the given [Row, Column] positions
cells_at(Rows, Positions, Cells) :-
    maplist({Rows}/[[R, C], V]>>(nth1(R, Rows, Row), nth1(C, Row, V)), Positions, Cells).

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

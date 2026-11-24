% csplib_067_quasigroup_completion: a SWI-Prolog model from DCP Rosetta.
%
% An order m quasigroup is a Latin square of size m. That is, an m x m multiplication table in which each element
% from 1 to m occurs exactly once in every row and every column. This problem asks to complete a partially filled
% quasigroup, given as start, in which 0 marks an empty cell.
%
% Save this file as model.pl. Download `csplib_067_quasigroup_completion.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_067_quasigroup_completion.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_067_quasigroup_completion.json')" -t halt model.pl
%
% Data fields: N (the order of the square), start (the square as given, a list of rows indexed from 0, where 0 marks
% an empty cell).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, Rows, [puzzle-Rows]) :-
    N = Instance.'N',
    Start = Instance.start,
    % Rows[I][J] is the number in row I and column J, from 1 to N
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 1..N), Rows),
    % each given cell keeps its value; an empty cell is left free
    maplist([Row, StartRow]>>maplist(given, Row, StartRow), Rows, Start),
    % each row holds each number once
    maplist(all_distinct, Rows),
    % each column holds each number once
    transpose(Rows, Columns),
    maplist(all_distinct, Columns).

% a given cell is fixed to its value; an empty cell (0) is left free
given(_, 0) :- !.
given(Cell, Value) :- Cell #= Value.

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

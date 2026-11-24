% csplib_003_quasigroup_existence: a SWI-Prolog model from DCP Rosetta.
%
% An order m quasigroup is a Latin square of size m: an m x m multiplication table in which each element occurs once
% in every row and once in every column. Find an order m quasigroup (with elements 0 to m-1) that satisfies the
% QG3 property, (a*b)*(b*a) = a for all a and b.
%
% Save this file as model.pl. Download `csplib_003_quasigroup_existence.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_003_quasigroup_existence.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_003_quasigroup_existence.json')" -t halt model.pl
%
% Data fields: m (the order of the quasigroup).
:- use_module(library(clpfd)).

model(Instance, Vars, [quasigroup-Rows]) :-
    M = Instance.m,
    Top is M - 1,
    % Rows[A][B] is the product a*b
    length(Rows, M),
    maplist(row_values(M, Top), Rows),
    % each element occurs once in every row and once in every column
    maplist(all_distinct, Rows),
    transpose(Rows, Columns),
    maplist(all_distinct, Columns),
    % the table flattened, so that the product of X and Y is at position X*M+Y+1
    append(Rows, Flat),
    Vars = Flat,
    % (a*b)*(b*a) = a for every pair a, b
    findall(A-B, (between(0, Top, A), between(0, Top, B)), Pairs),
    maplist(qg3(Flat, M), Pairs).

row_values(M, Top, Row) :-
    length(Row, M),
    Row ins 0..Top.

% (a*b)*(b*a) = a, looking the products up in the flattened table
qg3(Flat, M, A-B) :-
    AB_Index is A * M + B + 1,
    nth1(AB_Index, Flat, AB),
    BA_Index is B * M + A + 1,
    nth1(BA_Index, Flat, BA),
    Index #= AB * M + BA + 1,
    element(Index, Flat, A).

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

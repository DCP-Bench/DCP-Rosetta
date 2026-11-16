% csplib_050_diamond_free: a SWI-Prolog model from DCP Rosetta.
%
% Find a simple undirected graph on N vertices (no loops, no repeated edges) with no diamond as an induced subgraph:
% every set of four vertices has at most four edges between them. Each vertex has a degree that is greater than zero
% and divisible by 3, and the sum of the degrees is divisible by 12. Give the adjacency matrix.
%
% Save this file as model.pl. Download `csplib_050_diamond_free.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_050_diamond_free.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_050_diamond_free.json')" -t halt model.pl
%
% Data fields: N (the number of vertices).
:- use_module(library(clpfd)).

model(Instance, Vars, [matrix-Rows]) :-
    get_dict('N', Instance, N),
    length(Rows, N), maplist(length_is(N), Rows),   % Rows[I][J] = 1 when vertices I and J are adjacent
    append(Rows, Cells), Cells ins 0..1,
    % no loops: the diagonal is zero
    zero_diagonal(Rows, 1),
    % the graph is undirected: the matrix is symmetric
    transpose(Rows, Cols),
    maplist(same_row, Rows, Cols),
    % the degree of each vertex is greater than zero and divisible by 3
    maplist(degree_ok, Rows, Degrees),
    % the sum of the degrees is divisible by 12
    sum(Degrees, #=, Total),
    Total mod 12 #= 0,
    % no four vertices have five or more edges between them
    N1 is N - 1,
    findall([A, B, C, D],
            (between(0, N1, A), A1 is A + 1, between(A1, N1, B), B1 is B + 1,
             between(B1, N1, C), C1 is C + 1, between(C1, N1, D)),
            Quads),
    maplist(at_most_four_edges(Rows), Quads),
    append([Cells, Degrees, [Total]], Vars).

length_is(K, L) :- length(L, K).

zero_diagonal([], _).
zero_diagonal([Row|Rows], I) :-
    nth1(I, Row, 0),
    I1 is I + 1,
    zero_diagonal(Rows, I1).

same_row(Row, Col) :- maplist(#=, Row, Col).

degree_ok(Row, D) :-
    sum(Row, #=, D),
    D #> 0,
    D mod 3 #= 0.

at_most_four_edges(Rows, [A, B, C, D]) :-
    cell(Rows, A, B, E1), cell(Rows, A, C, E2), cell(Rows, A, D, E3),
    cell(Rows, B, C, E4), cell(Rows, B, D, E5), cell(Rows, C, D, E6),
    sum([E1, E2, E3, E4, E5, E6], #=<, 4).

cell(Rows, I, J, Value) :-
    nth0(I, Rows, Row),
    nth0(J, Row, Value).

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

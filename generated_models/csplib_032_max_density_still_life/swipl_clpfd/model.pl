% csplib_032_max_density_still_life: a SWI-Prolog model from DCP Rosetta.
%
% Find the most densely populated still life (a stable pattern of live and dead cells, which does not change from
% one generation of Conway's Game of Life to the next) on an n by m grid. Cells outside the grid are dead but still
% take part as neighbours. A live cell must have exactly 2 or 3 live neighbours to stay alive, and a dead cell,
% including a dead cell just outside the grid, must not have exactly 3 live neighbours. Maximise the number of live
% cells in the grid.
%
% Save this file as model.pl. Download `csplib_032_max_density_still_life.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_032_max_density_still_life.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_032_max_density_still_life.json')" -t halt model.pl
%
% Data fields: n (the number of rows of the grid), m (the number of columns of the grid).
:- use_module(library(clpfd)).

model(Instance, Vars, [grid-Rows], max(Total)) :-
    N = Instance.n, M = Instance.m,
    length(Rows, N), maplist(length_is(M), Rows),   % Rows[I][J] = 1 when the cell is alive
    append(Rows, Cells), Cells ins 0..1,
    % pad the grid with two rings of dead cells, so that every neighbour of a checked cell is in the padded array
    M4 is M + 4,
    length(Zero, M4), maplist(=(0), Zero),
    maplist(pad_row, Rows, PaddedRows),
    append([Zero, Zero|PaddedRows], [Zero, Zero], Padded),
    N2 is N + 2, M2 is M + 2,
    findall(I-J, (between(1, N2, I), between(1, M2, J)), Positions),   % the grid and the ring just outside it
    maplist(still_life_at(Padded), Positions),
    % the number of live cells, which is maximised
    sum(Cells, #=, Total),
    Vars = [Total|Cells].

length_is(K, L) :- length(L, K).

pad_row(Row, Padded) :- append([0, 0|Row], [0, 0], Padded).

% the eight offsets of the neighbours of a cell
offsets([(-1)-(-1), (-1)-0, (-1)-1, 0-(-1), 0-1, 1-(-1), 1-0, 1-1]).

still_life_at(Padded, I-J) :-
    cell(Padded, I, J, Alive),
    offsets(Offsets),
    maplist(neighbour(Padded, I, J), Offsets, Neighbours),
    sum(Neighbours, #=, Live),
    % a live cell has 2 or 3 live neighbours
    (Alive #= 1) #==> (Live #>= 2 #/\ Live #=< 3),
    % a dead cell does not have exactly 3 live neighbours
    (Alive #= 0) #==> (Live #\= 3).

neighbour(Padded, I, J, DI-DJ, Value) :-
    I2 is I + DI, J2 is J + DJ,
    cell(Padded, I2, J2, Value).

cell(Padded, I, J, Value) :-
    nth0(I, Padded, Row),
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

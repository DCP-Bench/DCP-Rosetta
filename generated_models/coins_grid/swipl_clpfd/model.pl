% coins_grid: a SWI-Prolog model from DCP Rosetta.
%
% On an n by n grid (a chessboard) place coins so that exactly c coins are in each row and exactly c coins in each
% column, with at most one coin in each cell. For a coin in row i and column j the squared horizontal distance from
% the main diagonal is (i - j)^2. Minimise the sum of these squared distances over all coins.
%
% Save this file as model.pl. Download `coins_grid.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('coins_grid.json')" -t halt model.pl
%
% Data fields: n (the side of the grid), c (the number of coins in each row and in each column).
:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(yall)).

model(Instance, Vars, [x-Rows, z-Z], min(Z)) :-
    N = Instance.n,
    C = Instance.c,
    % Rows[I][J] = 1 when a coin is placed in row I, column J; at most one coin per cell
    length(Rows, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 0..1), Rows),
    append(Rows, Cells),
    % exactly c coins in every row
    maplist({C}/[Row]>>sum(Row, #=, C), Rows),
    % exactly c coins in every column
    transpose(Rows, Columns),
    maplist({C}/[Column]>>sum(Column, #=, C), Columns),
    % the sum of the squared distances (i - j)^2 from the diagonal over the coins, in the same order as Cells
    findall(W, (between(1, N, I), between(1, N, J), W is (I - J) * (I - J)), Weights),
    scalar_product(Weights, Cells, #=, Z),
    Vars = [Z|Cells].

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

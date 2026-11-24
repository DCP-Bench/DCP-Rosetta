% csplib_023_magic_hexagon: a SWI-Prolog model from DCP Rosetta.
%
% A magic hexagon arranges the numbers 1 to 19 in a hexagon of cells A to S, laid out in five rows of 3, 4, 5, 4 and 3
% cells:
%       A  B  C
%     D  E  F  G
%   H  I  J  K  L
%     M  N  O  P
%       Q  R  S
% The sum of the numbers on each of the 15 lines (rows and diagonals) is the same magic constant, 38.
%
% Save this file as model.pl. Download `csplib_023_magic_hexagon.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_023_magic_hexagon.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_023_magic_hexagon.json')" -t halt model.pl
%
% Data fields: MAGIC_SUM (the sum of each line) and NUM_CELLS (the number of cells, 19).
:- use_module(library(clpfd)).

model(Instance, Vars, ['LD'-LD]) :-
    MagicSum = Instance.'MAGIC_SUM',
    NumCells = Instance.'NUM_CELLS',
    % LD is [A, B, ..., S], the numbers in the cells of the hexagon in the order of the statement
    LD = [A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S],
    length(LD, NumCells),
    % the numbers 1 to 19, each used once
    LD ins 1..NumCells,
    all_different(LD),
    Vars = LD,
    % the rows of the hexagon
    Rows = [[A, B, C], [D, E, F, G], [H, I, J, K, L], [M, N, O, P], [Q, R, S]],
    % the diagonals running down and to the left
    Left = [[A, D, H], [B, E, I, M], [C, F, J, N, Q], [G, K, O, R], [L, P, S]],
    % the diagonals running down and to the right
    Right = [[A, E, J, O, S], [B, F, K, P], [C, G, L], [D, I, N, R], [H, M, Q]],
    % each of the 15 lines sums to the magic constant
    append([Rows, Left, Right], Lines),
    maplist(line_sum(MagicSum), Lines).

line_sum(MagicSum, Line) :- sum(Line, #=, MagicSum).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
:- use_module(library(http/json)).
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

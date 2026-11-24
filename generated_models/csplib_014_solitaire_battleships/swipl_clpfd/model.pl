% csplib_014_solitaire_battleships: a SWI-Prolog model from DCP Rosetta.
%
% Solitaire battleships is played on a grid. The fleet consists of battleships (four squares long), cruisers (three
% squares), destroyers (two squares) and submarines (one square). Ships lie horizontally or vertically, and no two ships
% touch, not even diagonally. The numbers at the right of and below the grid give the number of squares of each row and
% column that are occupied by vessels. Some squares may be given as hints: water, a submarine, a part of a longer vessel
% (of unknown kind, not a submarine), or a particular part of a ship (left, right, top, bottom or middle).
%
% Save this file as model.pl. Download `csplib_014_solitaire_battleships.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_014_solitaire_battleships.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_014_solitaire_battleships.json')" -t halt model.pl
%
% Data fields: rows and cols (the number of rows and columns), rowsum and colsum (the occupied squares of each row and
% column), fleet_counts (for each ship length, the length and the number of ships of that length), hints (for each
% given square, its row, column and code, rows and columns indexed from 0), and the codes of the squares: WATER, CIRCLE
% (a submarine), LEFT, RIGHT, TOP, BOTTOM, MIDDLE (the parts of a ship) and _SHIP (any part of a longer vessel).
:- use_module(library(clpfd)).

model(Instance, Vars, [grid-Grid]) :-
    NR = Instance.rows,
    NC = Instance.cols,
    RowSum = Instance.rowsum,
    ColSum = Instance.colsum,
    Fleet = Instance.fleet_counts,
    Hints = Instance.hints,
    get_dict('WATER', Instance, W),
    get_dict('_SHIP', Instance, Ship),
    get_dict('CIRCLE', Instance, Ci),
    get_dict('LEFT', Instance, Le),
    get_dict('RIGHT', Instance, Ri),
    get_dict('TOP', Instance, To),
    get_dict('BOTTOM', Instance, Bo),
    get_dict('MIDDLE', Instance, Mi),
    Codes = codes(W, Ci, Le, Ri, To, Bo, Mi),
    % Grid[R][C] is the code of the square in row R and column C
    length(Grid, NR),
    maplist(grid_row(NC), Grid),
    term_variables(Grid, Vars),
    % a square holds water, a submarine or a part of a ship, never the generic _SHIP code
    Codes =.. [_|CodeList],
    maplist(one_of_codes(CodeList), Vars),
    maplist(#\=(Ship), Vars),
    % the shape of the ships: the squares around each square fit the square's own part
    cross_table(Codes, Table),
    numlist(1, NR, Rs),
    maplist(cross_rules(Grid, Codes, Table, NC), Rs),
    % no two ships touch, not even diagonally: the diagonal neighbours of a ship square are water
    maplist(diagonal_rules(Grid, Codes, NC), Rs),
    % the number of occupied squares in each row and column
    maplist(occupied_row(W), Grid, RowSum),
    transpose(Grid, Columns),
    maplist(occupied_row(W), Columns, ColSum),
    % the fleet: ships of each length
    maplist(fleet_rule(Grid, Codes), Fleet),
    % the fleet is all the ships: its squares are all the occupied squares, so no ship of another length (e.g. 5) exists
    findall(S, (member([Len, Num], Fleet), S is Len * Num), FleetSquares),
    sum_list(FleetSquares, Occupied),
    sum_list(RowSum, Occupied),
    % the hints
    maplist(hint_rule(Grid, Codes, Ship), Hints).

grid_row(NC, Row) :- length(Row, NC).

one_of_codes(Codes, V) :- element(_, Codes, V).

% the code of the square in row R and column C, water outside the grid
at(Grid, W, R, C, V) :-
    length(Grid, NR), Grid = [G1|_], length(G1, NC),
    (   R >= 1, R =< NR, C >= 1, C =< NC
    ->  cell(Grid, R, C, V)
    ;   V = W
    ).

cell(Grid, R, C, V) :- nth1(R, Grid, Row), nth1(C, Row, V).

% the allowed combinations of a square and its four orthogonal neighbours (up, down, left, right)
cross_table(codes(W, Ci, Le, Ri, To, Bo, Mi), Table) :-
    Codes = [W, Ci, Le, Ri, To, Bo, Mi],
    findall([X, U, D, L, R],
            ( member(X, Codes), member(U, Codes), member(D, Codes), member(L, Codes), member(R, Codes),
              cross_ok(codes(W, Ci, Le, Ri, To, Bo, Mi), X, U, D, L, R) ),
            Table).

cross_ok(codes(W, Ci, Le, Ri, To, Bo, Mi), X, U, D, L, R) :-
    (   X == W -> true
    ;   X == Ci -> U == W, D == W, L == W, R == W
    ;   X == Le -> memberchk(R, [Mi, Ri]), U == W, D == W, L == W
    ;   X == Ri -> memberchk(L, [Le, Mi]), U == W, D == W, R == W
    ;   X == To -> memberchk(D, [Mi, Bo]), U == W, L == W, R == W
    ;   X == Bo -> memberchk(U, [To, Mi]), D == W, L == W, R == W
    ;   X == Mi ->
        (   memberchk(L, [Le, Mi]), memberchk(R, [Ri, Mi]), U == W, D == W
        ;   memberchk(U, [To, Mi]), memberchk(D, [Bo, Mi]), L == W, R == W
        )
    ).

% the squares of row R, with their orthogonal neighbours, fit the table
cross_rules(Grid, Codes, Table, NC, R) :-
    Codes = codes(W, _, _, _, _, _, _),
    numlist(1, NC, Cs),
    maplist(cross_rule(Grid, W, Table, R), Cs).

cross_rule(Grid, W, Table, R, C) :-
    cell(Grid, R, C, X),
    R1 is R - 1, R2 is R + 1, C1 is C - 1, C2 is C + 1,
    at(Grid, W, R1, C, U),
    at(Grid, W, R2, C, D),
    at(Grid, W, R, C1, L),
    at(Grid, W, R, C2, Rt),
    tuples_in([[X, U, D, L, Rt]], Table).

% a square that is not water has water on each of its four diagonal neighbours
diagonal_rules(Grid, Codes, NC, R) :-
    Codes = codes(W, _, _, _, _, _, _),
    numlist(1, NC, Cs),
    maplist(diagonal_rule(Grid, W, R), Cs).

diagonal_rule(Grid, W, R, C) :-
    cell(Grid, R, C, X),
    R1 is R - 1, R2 is R + 1, C1 is C - 1, C2 is C + 1,
    at(Grid, W, R1, C1, D1), at(Grid, W, R1, C2, D2),
    at(Grid, W, R2, C1, D3), at(Grid, W, R2, C2, D4),
    (X #\= W) #==> (D1 #= W),
    (X #\= W) #==> (D2 #= W),
    (X #\= W) #==> (D3 #= W),
    (X #\= W) #==> (D4 #= W).

% the number of squares of a line that are not water
occupied_row(W, Line, Count) :-
    maplist(nonwater(W), Line, Ps),
    sum(Ps, #=, Count).

nonwater(W, X, P) :- P #<==> (X #\= W).

% the ships of a length, horizontal or vertical, and the submarines for length 1
fleet_rule(Grid, codes(W, Ci, Le, Ri, To, Bo, Mi), [Size, Count]) :-
    (   Size =:= 1
    ->  all_cells(Grid, Cells),
        maplist(code_is(Ci), Cells, Ps),
        sum(Ps, #=, Count)
    ;   starts(Grid, Size, codes(W, Ci, Le, Ri, To, Bo, Mi), Bs),
        sum(Bs, #=, Count)
    ).

all_cells(Grid, Cells) :- append(Grid, Cells).

code_is(Code, X, P) :- P #<==> (X #= Code).

% the start flags of the ships of length Size: horizontal from left to right, then vertical from top to bottom
starts(Grid, Size, Codes, Bs) :-
    length(Grid, NR), Grid = [G1|_], length(G1, NC),
    HMax is NC - Size + 1,
    VMax is NR - Size + 1,
    numlist(1, NR, Rs),
    numlist(1, NC, Cs),
    numlist(1, HMax, HCs),
    numlist(1, VMax, VRs),
    maplist(h_row_starts(Grid, Size, Codes, HCs), Rs, HBs),
    maplist(v_col_starts(Grid, Size, Codes, VRs), Cs, VBs),
    append(HBs, HFlags),
    append(VBs, VFlags),
    append(HFlags, VFlags, Bs).

h_row_starts(Grid, Size, Codes, HCs, R, Bs) :-
    maplist(h_start(Grid, Size, Codes, R), HCs, Bs).

v_col_starts(Grid, Size, Codes, VRs, C, Bs) :-
    maplist(v_start(Grid, Size, Codes, C), VRs, Bs).

h_start(Grid, Size, codes(_, _, Le, Ri, _, _, Mi), R, C, B) :-
    Last is C + Size - 1,
    numlist(C, Last, Cs),
    maplist(cell(Grid, R), Cs, Cells),
    Mids is Size - 2,
    length(MidCodes, Mids),
    maplist(=(Mi), MidCodes),
    append([[Le], MidCodes, [Ri]], Want),
    maplist(code_is_flag, Cells, Want, Ps),
    sum(Ps, #=, Sum),
    B #<==> (Sum #= Size).

v_start(Grid, Size, codes(_, _, _, _, To, Bo, Mi), C, R, B) :-
    Last is R + Size - 1,
    numlist(R, Last, Rs),
    maplist(cell_in_col(Grid, C), Rs, Cells),
    Mids is Size - 2,
    length(MidCodes, Mids),
    maplist(=(Mi), MidCodes),
    append([[To], MidCodes, [Bo]], Want),
    maplist(code_is_flag, Cells, Want, Ps),
    sum(Ps, #=, Sum),
    B #<==> (Sum #= Size).

cell_in_col(Grid, C, R, V) :- cell(Grid, R, C, V).

code_is_flag(X, Code, P) :- P #<==> (X #= Code).

% the hint square has the given code; the generic _SHIP code means any part of a longer vessel (not water, not a submarine)
hint_rule(Grid, codes(W, Ci, _, _, _, _, _), Ship, [R, C, Code]) :-
    R1 is R + 1, C1 is C + 1,
    cell(Grid, R1, C1, V),
    (   Code =:= Ship
    ->  V #\= W, V #\= Ci
    ;   V #= Code
    ).

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

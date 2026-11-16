% calvin_puzzle: a SWI-Prolog model from DCP Rosetta.
%
% Fill an n by n grid with the numbers 1 to n*n, each used once and in sequence, starting from any square. Each next
% number is placed by one of two moves. If it is placed vertically or horizontally, it is exactly three squares away
% from the previous number (two squares lie between them). If it is placed diagonally, it is exactly two squares away
% from the previous number (one square lies between them).
%
% Save this file as model.pl. Download `calvin_puzzle.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/calvin_puzzle.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('calvin_puzzle.json')" -t halt model.pl
%
% Data fields: n (the side of the grid).
:- use_module(library(clpfd)).

model(Instance, Vars, [x-Rows]) :-
    N = Instance.n,
    Squares is N * N,
    numlist(1, Squares, Numbers),           % the numbers 1 to n*n, in sequence
    % the legal moves between two squares, numbered 1 to n*n row by row
    findall([A, B], (between(1, Squares, A), between(1, Squares, B), step(N, A, B)), Steps),
    % Cells[K]: the square (numbered from 1) holding the number K
    length(Cells, Squares),
    Cells ins 1..Squares,
    all_distinct(Cells),                    % each square holds one number
    % each number after the first sits one legal move from the number before it
    append(Earlier, [_], Cells),
    Cells = [_|Later],
    maplist(legal_move(Steps), Earlier, Later),
    % Grid[S]: the number on square S
    length(Grid, Squares),
    Grid ins 1..Squares,
    maplist(on_square(Grid), Numbers, Cells),   % number K sits on the square Cells[K]
    grid_rows(Grid, N, Rows),
    append(Cells, Grid, Vars).

% Square A to square B is a legal move: three squares along a row or a column, or two squares along both.
step(N, A, B) :-
    cell(N, A, RA, CA),
    cell(N, B, RB, CB),
    DR is abs(RA - RB),
    DC is abs(CA - CB),
    (   DR =:= 0, DC =:= 3
    ;   DR =:= 3, DC =:= 0
    ;   DR =:= 2, DC =:= 2
    ).

% The row and column (counted from 0) of square A, numbered from 1 row by row.
cell(N, A, R, C) :-
    R is (A - 1) // N,
    C is (A - 1) mod N.

% The move from square A to square B is legal.
legal_move(Steps, A, B) :-
    tuples_in([[A, B]], Steps).

% The number Number is on square Square.
on_square(Grid, Number, Square) :-
    element(Square, Grid, Number).

% Flat list of squares, row by row, cut into rows of length N.
grid_rows([], _, []).
grid_rows(Flat, N, [Row|Rows]) :-
    length(Row, N),
    append(Row, Rest, Flat),
    grid_rows(Rest, N, Rows).

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

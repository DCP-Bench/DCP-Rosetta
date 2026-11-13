% csplib_021_crossfigures: an ECLiPSe model from DCP Rosetta.
%
% Crossfigures are the numerical equivalent of crosswords. A 9 by 9 grid has black cells (X), white cells, and numbered
% white cells. Each across or down run of white cells reads as a number, with no leading zero, and each clue gives the
% answer to the numbered run that starts at its cell. Fill every white cell with a digit so that every clue holds. Each
% answer is a whole number whose digits are the digits of its run, and a digit may be 0.
%
%   1  2  3  4  5  6  7  8  9
%   ---------------------------
%   1  2  _  3  X  4  _  5  6    1
%   7  _  X  8  _  _  X  9  _    2
%   _  X  10 _  X  11 12 X  _    3
%   13 14 _  _  X  15 _  16 _    4
%   X  _  X  X  X  X  X  _  X    5
%   17 _  18 19 X  20 21 _  22   6
%   _  X  23 _  X  24 _  X  _    7
%   25 26 X  27 _  _  X  28 _    8
%   29 _  _  _  X  30 _  _  _    9
%
% Across: 1 27 across times two; 4 4 down plus seventy-one; 7 18 down plus four; 8 6 down divided by sixteen;
% 9 2 down minus eighteen; 10 dozen in six gross; 11 5 down minus seventy; 13 26 down times 23 across; 15 6 down minus
% 350; 17 25 across times 23 across; 20 a square number; 23 a prime number; 24 a square number; 25 20 across divided
% by seventeen; 27 6 down divided by four; 28 four dozen; 29 seven gross; 30 22 down plus 450.
% Down: 1 1 across plus twenty-seven; 2 five dozen; 3 30 across plus 888; 4 two times 17 across; 5 29 across divided
% by twelve; 6 28 across times 23 across; 10 10 across plus four; 12 three times 24 across; 14 13 across divided by
% sixteen; 16 28 down times fifteen; 17 13 across minus 399; 18 29 across divided by eighteen; 19 22 down minus
% ninety-four; 20 20 across minus nine; 21 25 across minus fifty-two; 22 20 down times six; 26 five times 24 across;
% 28 21 down plus twenty-seven.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
% Save this model as model.ecl and run it (ECLiPSe 7.2, https://eclipseclp.org) with:
%   eclipse -b model.ecl -e "run, halt"

% The grid layout is given below in cf_tokens: x is a black cell, w a white cell without a clue number, and an integer
% a white cell with that clue number. Output M: the digit of each cell, 0 for the black cells.

:- lib(ic).

cf_tokens([
    [1,2,w,3,x,4,w,5,6],
    [7,w,x,8,w,w,x,9,w],
    [w,x,10,w,x,11,12,x,w],
    [13,14,w,w,x,15,w,16,w],
    [x,w,x,x,x,x,x,w,x],
    [17,w,18,19,x,20,21,w,22],
    [w,x,23,w,x,24,w,x,w],
    [25,26,x,27,w,w,x,28,w],
    [29,w,w,w,x,30,w,w,w]
]).

model(_Instance, Vars, ['M'-DRows]) :-
    cf_tokens(Toks),
    % one digit variable per white cell, 0 for black cells
    cf_make_rows(Toks, DRows),
    cf_flat_vars(DRows, Vars),
    % the answer of each across and down run
    cf_across_starts(AS),
    cf_down_starts(DS),
    cf_answers(AS, across, DRows, As),
    cf_answers(DS, down, DRows, Ds),
    % the clues
    cf_clues(As, Ds).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).

% ---- grid of digits -------------------------------------------------------

cf_make_rows([], []).
cf_make_rows([T|Ts], [D|Ds]) :-
    cf_make_cells(T, D),
    cf_make_rows(Ts, Ds).

cf_make_cells([], []).
cf_make_cells([x|Ts], [0|Ds]) :- !,
    cf_make_cells(Ts, Ds).
cf_make_cells([_|Ts], [V|Ds]) :-
    V :: 0..9,
    cf_make_cells(Ts, Ds).

cf_flat_vars([], []).
cf_flat_vars([Row|Rows], Vs) :-
    cf_row_vars(Row, Vs, Vs1),
    cf_flat_vars(Rows, Vs1).

cf_row_vars([], Vs, Vs).
cf_row_vars([V|Vs0], [V|Vs], Out) :- var(V), !,
    cf_row_vars(Vs0, Vs, Out).
cf_row_vars([_|Vs0], Vs, Out) :-
    cf_row_vars(Vs0, Vs, Out).

% the integers L to H, each once
cf_range(L, H, X) :-
    L =< H,
    (   X = L
    ;   L < H,
        L1 is L+1,
        cf_range(L1, H, X)
    ).

cf_pick(1, [X|_], X) :- !.
cf_pick(N, [_|T], X) :-
    N1 is N-1,
    cf_pick(N1, T, X).

cf_tok(R, C, T) :-
    cf_tokens(Toks),
    cf_pick(R, Toks, Row),
    cf_pick(C, Row, T).

% a cell is white when it is not black (x)
cf_white(R, C) :-
    R >= 1, R =< 9, C >= 1, C =< 9,
    cf_tok(R, C, T),
    T \== x.

cf_cell(DRows, R, C, V) :-
    cf_pick(R, DRows, Row),
    cf_pick(C, Row, V).

% ---- runs -----------------------------------------------------------------

% Lab-R-C for each across run start: a numbered white cell whose left neighbour is not white and whose right
% neighbour is white.
cf_across_starts(Ss) :-
    findall(Lab-R-C,
            ( cf_range(1, 9, R), cf_range(1, 9, C),
              cf_across_start(R, C, Lab) ),
            Ss).

% Lab-R-C for each down run start: a numbered white cell whose upper neighbour is not white and whose lower
% neighbour is white.
cf_down_starts(Ss) :-
    findall(Lab-R-C,
            ( cf_range(1, 9, R), cf_range(1, 9, C),
              cf_down_start(R, C, Lab) ),
            Ss).

cf_across_start(R, C, Lab) :-
    cf_tok(R, C, Lab), integer(Lab),
    cf_left_free(R, C),
    C1 is C+1, cf_white(R, C1).

cf_down_start(R, C, Lab) :-
    cf_tok(R, C, Lab), integer(Lab),
    cf_up_free(R, C),
    R1 is R+1, cf_white(R1, C).

cf_left_free(R, C) :-
    ( C =:= 1 -> true ; C0 is C-1, \+ cf_white(R, C0) ).

cf_up_free(R, C) :-
    ( R =:= 1 -> true ; R0 is R-1, \+ cf_white(R0, C) ).

% the digits of the across run starting at (R, C)
cf_acells(DRows, R, C, [V|Vs]) :-
    cf_cell(DRows, R, C, V),
    C1 is C+1,
    ( cf_white(R, C1) -> cf_acells(DRows, R, C1, Vs) ; Vs = [] ).

% the digits of the down run starting at (R, C)
cf_dcells(DRows, R, C, [V|Vs]) :-
    cf_cell(DRows, R, C, V),
    R1 is R+1,
    ( cf_white(R1, C) -> cf_dcells(DRows, R1, C, Vs) ; Vs = [] ).

cf_cells(across, DRows, R, C, Vs) :- cf_acells(DRows, R, C, Vs).
cf_cells(down, DRows, R, C, Vs) :- cf_dcells(DRows, R, C, Vs).

% one answer variable per run, equal to the number its digits spell, with no leading zero
cf_answers([], _, _, []).
cf_answers([Lab-R-C|Ss], Dir, DRows, [Lab-Ans|Ps]) :-
    cf_cells(Dir, DRows, R, C, Vs),
    length(Vs, L),
    Lo is 10^(L-1),
    Hi is 10^L - 1,
    Ans :: Lo..Hi,
    cf_post_number(Vs, Ans),
    cf_answers(Ss, Dir, DRows, Ps).

% the answer is the number its digits spell; written out per length, since a sum built at run time is refused by ic
cf_post_number([D1, D2], A) :-
    A #= 10*D1 + D2.
cf_post_number([D1, D2, D3], A) :-
    A #= 100*D1 + 10*D2 + D3.
cf_post_number([D1, D2, D3, D4], A) :-
    A #= 1000*D1 + 100*D2 + 10*D3 + D4.

% the answer of the numbered run N
ga(N, As, V) :- memberchk(N-V, As).
gd(N, Ds, V) :- memberchk(N-V, Ds).

% a square number: the square of some Y from 0 to 99
cf_square(X) :-
    Y :: 0..99,
    X #= Y*Y.

% a prime number, among the two-digit primes (every answer here that is prime is two digits)
cf_prime(X) :-
    X :: [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97].

% ---- clues ----------------------------------------------------------------

cf_clues(As, Ds) :-
    ga(1, As, A1), ga(4, As, A4), ga(7, As, A7), ga(8, As, A8), ga(9, As, A9),
    ga(10, As, A10), ga(11, As, A11), ga(13, As, A13), ga(15, As, A15),
    ga(17, As, A17), ga(20, As, A20), ga(23, As, A23), ga(24, As, A24),
    ga(25, As, A25), ga(27, As, A27), ga(28, As, A28), ga(29, As, A29),
    ga(30, As, A30),
    gd(1, Ds, D1), gd(2, Ds, D2), gd(3, Ds, D3), gd(4, Ds, D4), gd(5, Ds, D5),
    gd(6, Ds, D6), gd(10, Ds, D10), gd(12, Ds, D12), gd(14, Ds, D14),
    gd(16, Ds, D16), gd(17, Ds, D17), gd(18, Ds, D18), gd(19, Ds, D19),
    gd(20, Ds, D20), gd(21, Ds, D21), gd(22, Ds, D22), gd(26, Ds, D26),
    gd(28, Ds, D28),

    % 1 across: 27 across times two
    A1 #= 2*A27,
    % 4 across: 4 down plus seventy-one
    A4 #= D4 + 71,
    % 7 across: 18 down plus four
    A7 #= D18 + 4,
    % 8 across: 6 down divided by sixteen
    D6 #= 16*A8,
    % 9 across: 2 down minus eighteen
    A9 #= D2 - 18,
    % 10 across: dozen in six gross (six gross is 864, which is 72 dozen)
    A10 #= 72,
    % 11 across: 5 down minus seventy
    A11 #= D5 - 70,
    % 13 across: 26 down times 23 across
    A13 #= D26*A23,
    % 15 across: 6 down minus 350
    A15 #= D6 - 350,
    % 17 across: 25 across times 23 across
    A17 #= A25*A23,
    % 20 across: a square number
    cf_square(A20),
    % 23 across: a prime number
    cf_prime(A23),
    % 24 across: a square number
    cf_square(A24),
    % 25 across: 20 across divided by seventeen
    A20 #= 17*A25,
    % 27 across: 6 down divided by four
    D6 #= 4*A27,
    % 28 across: four dozen
    A28 #= 48,
    % 29 across: seven gross
    A29 #= 1008,
    % 30 across: 22 down plus 450
    A30 #= D22 + 450,

    % 1 down: 1 across plus twenty-seven
    D1 #= A1 + 27,
    % 2 down: five dozen
    D2 #= 60,
    % 3 down: 30 across plus 888
    D3 #= A30 + 888,
    % 4 down: two times 17 across
    D4 #= 2*A17,
    % 5 down: 29 across divided by twelve
    A29 #= 12*D5,
    % 6 down: 28 across times 23 across
    D6 #= A28*A23,
    % 10 down: 10 across plus four
    D10 #= A10 + 4,
    % 12 down: three times 24 across
    D12 #= 3*A24,
    % 14 down: 13 across divided by sixteen
    A13 #= 16*D14,
    % 16 down: 28 down times fifteen
    D16 #= 15*D28,
    % 17 down: 13 across minus 399
    D17 #= A13 - 399,
    % 18 down: 29 across divided by eighteen
    A29 #= 18*D18,
    % 19 down: 22 down minus ninety-four
    D19 #= D22 - 94,
    % 20 down: 20 across minus nine
    D20 #= A20 - 9,
    % 21 down: 25 across minus fifty-two
    D21 #= A25 - 52,
    % 22 down: 20 down times six
    D22 #= 6*D20,
    % 26 down: five times 24 across
    D26 #= 5*A24,
    % 28 down: 21 down plus twenty-seven
    D28 #= D21 + 27.

:- lib(branch_and_bound).

run :- solve_model([]).

solve_model(Instance) :-
    (   current_module(gfd) -> Lib = gfd ; Lib = ic ),
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   Objective = max(Expr)
    ->  call(Lib:(Total #= Expr)), call(Lib:(Cost #= -Total)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   Objective = min(Expr)
    ->  call(Lib:(Cost #= Expr)),
        minimize(run_search(Vars, Outputs), Cost)
    ;   run_search(Vars, Outputs)
    ),
    ( foreach(Name-Value, Outputs) do printf("%w = %w%n", [Name, Value]) ).

run_search(Vars, Outputs) :-
    (   current_predicate(search_goal/1) -> search_goal(Vars) ; labeling(Vars) ),
    term_variables(Outputs, Free),
    labeling(Free).

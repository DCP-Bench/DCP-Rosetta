% csplib_021_crossfigures: a SWI-Prolog model from DCP Rosetta.
%
% Crossfigures are the numerical equivalent of crosswords: a grid of numbered cells and clues whose numerical answers
% are placed on the grid. Each cell marked X holds 0, and every other cell holds a digit of an answer (a digit may be 0).
% The answers are the across and down numbers read from their cells, and each answer must satisfy its clue.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
% Save this model as model.pl and run it (SWI-Prolog 9, https://www.swi-prolog.org) with:
%   swipl -g "solve_model(_{})" -t halt model.pl
%
% The grid is the one in the statement, written below with the labels of its numbered cells, b for an empty cell and
% x for a cell marked X. The clues are written as constraints on the across (A) and down (D) answers, named by their
% numbers. An answer is read from its cells left to right or top to bottom, and has no leading zero.
:- use_module(library(clpfd)).

% the grid: numbered cells, b (an empty cell) and x (a cell marked X)
grid([[1, 2, b, 3, x, 4, b, 5, 6],
      [7, b, x, 8, b, b, x, 9, b],
      [b, x, 10, b, x, 11, 12, x, b],
      [13, 14, b, b, x, 15, b, 16, b],
      [x, b, x, x, x, x, x, b, x],
      [17, b, 18, 19, x, 20, 21, b, 22],
      [b, x, 23, b, x, 24, b, x, b],
      [25, 26, x, 27, b, b, x, 28, b],
      [29, b, b, b, x, 30, b, b, b]]).

model(_, Vars, ['M'-Rows]) :-
    grid(G),
    maplist(build_row, G, Rows),
    % the across answers (A) and the down answers (D), each a number read from its cells
    Acr = [1-A1, 4-A4, 7-A7, 8-A8, 9-A9, 10-A10, 11-A11, 13-A13, 15-A15, 17-A17, 20-A20, 23-A23, 24-A24,
           25-A25, 27-A27, 28-A28, 29-A29, 30-A30],
    Dwn = [1-D1, 2-D2, 3-D3, 4-D4, 5-D5, 6-D6, 10-D10, 12-D12, 14-D14, 16-D16, 17-D17, 18-D18, 19-D19,
           20-D20, 21-D21, 22-D22, 26-D26, 28-D28],
    maplist(bind_word(G, Rows, across), Acr),
    maplist(bind_word(G, Rows, down), Dwn),
    % 1 across: 27 across times two
    A1 #= 2 * A27,
    % 4 across: 4 down plus seventy-one
    A4 #= D4 + 71,
    % 7 across: 18 down plus four
    A7 #= D18 + 4,
    % 8 across: 6 down divided by sixteen
    D6 #= 16 * A8,
    % 9 across: 2 down minus eighteen
    A9 #= D2 - 18,
    % 10 across: dozen in six gross (six gross is 72 dozen)
    A10 #= 72,
    % 11 across: 5 down minus seventy
    A11 #= D5 - 70,
    % 13 across: 26 down times 23 across
    A13 #= D26 * A23,
    % 15 across: 6 down minus 350
    A15 #= D6 - 350,
    % 17 across: 25 across times 23 across
    A17 #= A25 * A23,
    % 20 across: a square number
    square(A20, S20),
    % 23 across: a prime number
    prime_dom(PrimeDom),
    A23 in PrimeDom,
    % 24 across: a square number
    square(A24, S24),
    % 25 across: 20 across divided by seventeen
    A20 #= 17 * A25,
    % 27 across: 6 down divided by four
    D6 #= 4 * A27,
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
    D4 #= 2 * A17,
    % 5 down: 29 across divided by twelve
    A29 #= 12 * D5,
    % 6 down: 28 across times 23 across
    D6 #= A28 * A23,
    % 10 down: 10 across plus four
    D10 #= A10 + 4,
    % 12 down: three times 24 across
    D12 #= 3 * A24,
    % 14 down: 13 across divided by sixteen
    A13 #= 16 * D14,
    % 16 down: 28 down times fifteen
    D16 #= D28 * 15,
    % 17 down: 13 across minus 399
    D17 #= A13 - 399,
    % 18 down: 29 across divided by eighteen
    A29 #= 18 * D18,
    % 19 down: 22 down minus ninety-four
    D19 #= D22 - 94,
    % 20 down: 20 across minus nine
    D20 #= A20 - 9,
    % 21 down: 25 across minus fifty-two
    D21 #= A25 - 52,
    % 22 down: 20 down times six
    D22 #= D20 * 6,
    % 26 down: five times 24 across
    D26 #= 5 * A24,
    % 28 down: 21 down plus twenty-seven
    D28 #= D21 + 27,
    term_variables([Rows, S20, S24], Vars).

% a cell of an empty or numbered position holds a digit, a blocked cell holds 0
build_row(Row, Cells) :- maplist(build_cell, Row, Cells).
build_cell(x, 0) :- !.
build_cell(_, V) :- V in 0..9.

% the answer of the word that starts at the cell labelled N and runs across or down, as a number
bind_word(G, Rows, Dir, N-V) :-
    dir(Dir, DR, DC),
    word_cells(G, Rows, N, DR, DC, Cells),
    length(Cells, L),
    powers(L, Ps),
    scalar_product(Ps, Cells, #=, V),
    Cells = [First|_],
    First #\= 0.

dir(across, 0, 1).
dir(down, 1, 0).

powers(L, Ps) :- findall(P, (between(1, L, I), P is 10 ^ (L - I)), Ps).

% the cells of the word from the cell labelled N, up to the first blocked cell
word_cells(G, Rows, N, DR, DC, Cells) :-
    cell(G, R, C, N),
    walk(G, Rows, R, C, DR, DC, Cells).

walk(G, Rows, R, C, DR, DC, Cells) :-
    (   R >= 1, R =< 9, C >= 1, C =< 9, cell(G, R, C, Gv), Gv \== x
    ->  cell(Rows, R, C, V),
        Cells = [V|More],
        R1 is R + DR,
        C1 is C + DC,
        walk(G, Rows, R1, C1, DR, DC, More)
    ;   Cells = []
    ).

cell(Grid, R, C, V) :- nth1(R, Grid, Row), nth1(C, Row, V).

% S is a number whose square is X
square(X, S) :- S in 0..99, X #= S * S.

% the domain of the prime numbers from 11 to 99
prime_dom(Dom) :-
    findall(P, (between(11, 99, P), \+ (between(2, 9, D), D < P, P mod D =:= 0)), Ps),
    union_dom(Ps, Dom).

union_dom([P], P) :- !.
union_dom([P|Ps], P \/ D) :- union_dom(Ps, D).

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

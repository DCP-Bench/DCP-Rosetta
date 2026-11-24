% csplib_015_schurs_lemma: an ECLiPSe model from DCP Rosetta.
%
% Put the n balls labelled 1, ..., n into c boxes so that for any triple of balls (x, y, z) with x + y = z, where x and
% y may be equal, not all three are in the same box.
%
% Save this file as model.ecl. Download `csplib_015_schurs_lemma.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_015_schurs_lemma.json
%   eclipse -b model.ecl -e "run('csplib_015_schurs_lemma_1.dat'), halt"

% Instance fields: n (the number of balls) and c (the number of boxes). Output balls: balls[I] is the box, from 1 to c,
% that ball I is put in (balls are numbered from 1, the list from 0).

:- lib(ic).
:- lib(listut).

model(Instance, Balls, [balls-Balls]) :-
    memberchk(n-N, Instance),
    memberchk(c-C, Instance),
    length(Balls, N),
    % each ball is in one of the boxes 1 to C
    Balls :: 1..C,
    % InBox[I][J] is 1 exactly when ball I+1 is in box J
    ( foreach(B, Balls), foreach(Row, InBox), param(C) do
        boxes_of(B, 1, C, Row)
    ),
    % for any triple of balls x, y, z with x + y = z, not all three are in the same box
    post_x(1, N, InBox).

% boxes_of(+Ball, +J, +C, -Ms): Ms holds, for the boxes J to C, the 0/1 flag "Ball is in box J"
boxes_of(B, J, C, Ms) :-
    ( J > C ->
        Ms = []
    ;   Ms = [M|Ms1],
        M #= (B #= J),
        J1 is J + 1,
        boxes_of(B, J1, C, Ms1)
    ).

% the triples x <= y with z = x + y <= N
post_x(X, N, InBox) :-
    ( X > N ->
        true
    ;   post_y(X, X, N, InBox),
        X1 is X + 1,
        post_x(X1, N, InBox)
    ).

post_y(X, Y, N, InBox) :-
    ( Y > N ->
        true
    ;   Z is X + Y,
        ( Z =< N ->
            post_triple(X, Y, Z, InBox)
        ;   true
        ),
        Y1 is Y + 1,
        post_y(X, Y1, N, InBox)
    ).

% in every box, at most two of the three balls x, y and z are present
post_triple(X, Y, Z, InBox) :-
    nth1(X, InBox, RX),
    nth1(Y, InBox, RY),
    nth1(Z, InBox, RZ),
    ( foreach(Mx, RX), foreach(My, RY), foreach(Mz, RZ) do
        Mx + My + Mz #=< 2
    ).

search_goal(Balls) :-
    search(Balls, 0, first_fail, indomain_min, complete, []).

:- lib(branch_and_bound).

% Reads the data file, builds the model, solves it and prints each output.
run(File) :-
    open(File, read, Stream), read(Stream, Instance), close(Stream),
    solve_model(Instance).

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

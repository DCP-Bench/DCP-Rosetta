% csplib_039_rehearsal: an ECLiPSe model from DCP Rosetta.
%
% A concert consists of a number of pieces of music of different durations, each involving a different combination of the
% members of the orchestra. Players arrive at rehearsals immediately before the first piece in which they are involved
% and depart immediately after the last piece in which they are involved. Devise an order in which the pieces can be
% rehearsed so as to minimise the total time that players are waiting to play: the total time when players are present
% but not currently playing.
%
% Save this file as model.ecl. Download `csplib_039_rehearsal.json` and `dcp_convert_ecl.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
% Convert the instances once, then run the first one (ECLiPSe 7.2, https://eclipseclp.org):
%   python dcp_convert_ecl.py csplib_039_rehearsal.json
%   eclipse -b model.ecl -e "run('csplib_039_rehearsal_1.dat'), halt"
%
% The instance fields: duration (the duration of each piece, indexed from 0), num_pieces (the number of pieces),
% num_players (the number of players), rehearsal (rehearsal[P][J] is 1 when player P plays in piece J, both indexed from 0).

:- lib(ic).
:- lib(branch_and_bound).

% Output rehearsal_order: the piece rehearsed in each slot, slots and pieces indexed from 0.
model(Instance, Vars, [rehearsal_order-Ord], min(Cost)) :-
    memberchk(duration-Durs, Instance),
    memberchk(num_pieces-P, Instance),
    memberchk(num_players-NP, Instance),
    memberchk(rehearsal-Rehearsal, Instance),
    int_sum(Durs, SumD),
    ids(P, Ids),

    % the slot of each piece, all slots different
    length(Pos, P),
    Pos :: 0..P-1,
    alldifferent(Pos),

    % the start of each piece: the total duration of the pieces rehearsed before it
    ( foreach(PJ, Pos), foreach(Start, Starts), param(Pos, Durs) do
        ( foreach(PK, Pos), foreach(Dk, Durs), foreach(T, Ts), param(PJ) do
            Before #= (PK #< PJ),
            T #= Dk * Before
        ),
        Start #= sum(Ts)
    ),

    % the end of each piece: its start plus its duration
    ( foreach(S, Starts), foreach(Dj, Durs), foreach(E, Ends) do E #= S + Dj ),

    % each player arrives before the start of the first piece it plays in and leaves after the end of the last one
    length(Firsts, NP), Firsts :: 0..SumD,
    length(Lasts, NP), Lasts :: 0..SumD,
    ( foreach(Row, Rehearsal), foreach(F, Firsts), foreach(L, Lasts), param(Starts, Ends) do
        ( foreach(X, Row), foreach(S, Starts), foreach(E, Ends), param(F, L) do
            ( X =:= 1 -> F #=< S, L #>= E ; true )
        )
    ),

    % the waiting time: the time each player is present, minus the time it plays
    played_time(Rehearsal, Durs, Played),
    Cost #= sum(Lasts) - sum(Firsts) - Played,

    % the piece rehearsed in each slot
    length(Ord, P),
    Ord :: 0..P-1,
    ( for(Slot, 0, P - 1), foreach(O, Ord), param(Pos, Ids) do
        ( foreach(PJ, Pos), foreach(J, Ids), foreach(T, Ts), param(Slot) do
            At #= (PJ #= Slot),
            T #= J * At
        ),
        O #= sum(Ts)
    ),
    append(Pos, Firsts, Vars1),
    append(Vars1, Lasts, Vars).

% the total time the players play: each player plays the pieces it is involved in
played_time([], _, 0).
played_time([Row|Rows], Durs, Total) :-
    played_time(Rows, Durs, Rest),
    dot(Row, Durs, Here),
    Total is Rest + Here.

dot([], [], 0).
dot([X|Xs], [D|Ds], Total) :-
    dot(Xs, Ds, Rest),
    Total is Rest + X * D.

int_sum([], 0).
int_sum([X|Xs], Total) :-
    int_sum(Xs, Rest),
    Total is Rest + X.

% the list 0, 1, ..., P-1
ids(P, Ids) :-
    Last is P - 1,
    ids_(0, Last, Ids).

ids_(I, Last, []) :- I > Last, !.
ids_(I, Last, [I|Is]) :-
    I1 is I + 1,
    ids_(I1, Last, Is).

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

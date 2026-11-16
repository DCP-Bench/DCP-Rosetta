% csplib_039_rehearsal: a SWI-Prolog model from DCP Rosetta.
%
% A concert consists of pieces of music of different durations, each involving a different combination of the
% players. A player arrives immediately before the first piece in which they play and leaves immediately after the
% last one. Find an order of the pieces to rehearse that minimises the total time the players spend waiting, that is
% the total time they are present but not playing.
%
% Save this file as model.pl. Download `csplib_039_rehearsal.json` from the problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
% Run the first instance (SWI-Prolog 9, https://www.swi-prolog.org), or the second with solve_file(..., 2):
%   swipl -g "solve_file('csplib_039_rehearsal.json')" -t halt model.pl
%
% Data fields: num_pieces (the number of pieces N), num_players (the number of players), duration (the duration of
% each piece, lists indexed from 0), rehearsal (rehearsal[P][J] is 1 when player P plays in piece J, indexed from 0).
:- use_module(library(clpfd)).

model(Instance, Vars, [rehearsal_order-Order], min(Total)) :-
    N = Instance.num_pieces,
    N1 is N - 1,
    Durs = Instance.duration,
    Flags = Instance.rehearsal,
    sum_list(Durs, Horizon),
    % Pos[J]: the slot (from 1) in which piece J is rehearsed; Starts[J]: the time piece J starts
    length(Pos, N), Pos ins 1..N, all_distinct(Pos),
    length(Starts, N), Starts ins 0..Horizon,
    maplist(piece_at, Pos, Starts, Durs, Pieces),
    no_overlap_pairs(Pieces),
    % Order[I]: the piece rehearsed in slot I (from 0), which is the inverse of Pos
    length(Order, N), Order ins 0..N1,
    numlist(0, N1, Ids),
    maplist(in_slot(Order), Pos, Ids),
    % each player is present from the start of the first piece they play to the end of the last one
    length(Flags, NP),
    length(Ss, NP), length(Es, NP),
    Ss ins 0..Horizon, Es ins 0..Horizon,
    maplist(player_span(Pieces), Flags, Ss, Es),
    maplist(span, Ss, Es, Spans),
    % the waiting time is the presence of the players minus the time they play
    maplist(played_time(Durs), Flags, PlayedEach),
    sum_list(PlayedEach, Played),
    sum(Spans, #=, Present),
    Total #= Present - Played,
    length(Spans, NP),
    append([Pos, Starts, Order, Ss, Es, Spans, [Present, Total]], Vars).

piece_at(P, S, D, piece(P, S, D)).

% the pieces are rehearsed one at a time: a piece in an earlier slot ends before a piece in a later slot starts
no_overlap_pairs([]).
no_overlap_pairs([X|Xs]) :-
    maplist(no_overlap(X), Xs),
    no_overlap_pairs(Xs).

no_overlap(piece(P1, S1, D1), piece(P2, S2, D2)) :-
    (P1 #< P2) #==> (S2 #>= S1 + D1),
    (P2 #< P1) #==> (S1 #>= S2 + D2).

in_slot(Order, Slot, Id) :- element(Slot, Order, Id).

% the player is present from the start of the first piece they play to the end of the last one
player_span(Pieces, Flags, S, E) :-
    S #=< E,
    maplist(present(S, E), Flags, Pieces).

present(S, E, 1, piece(_, St, D)) :-
    S #=< St,
    E #>= St + D.
present(_, _, 0, _).

span(S, E, D) :- D #= E - S.

played_time(Durs, Row, Time) :-
    maplist(mul, Row, Durs, Products),
    sum_list(Products, Time).

mul(F, D, P) :- P is F*D.

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

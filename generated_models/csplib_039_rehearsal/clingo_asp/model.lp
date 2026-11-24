% csplib_039_rehearsal: a clingo model from DCP Rosetta.
%
% A concert is to consist of a number of pieces of music of different durations, each involving a different combination
% of the members of the orchestra. Players can arrive at rehearsals immediately before the first piece in which they are
% involved and depart immediately after the last piece in which they are involved. The problem is to devise an order in
% which the pieces can be rehearsed so as to minimize the total time that players are waiting to play, i.e. the total time
% when players are present but not currently playing.
%
% Save this file as model.lp. Download `csplib_039_rehearsal.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_039_rehearsal.json
%   python -m clingo model.lp csplib_039_rehearsal_1.lp

% Input: num_pieces(N): the number N of pieces; num_players(M): the number M of players;
% duration(P, D): the duration D of piece P; rehearsal(Q, P, V): V is 1 when player Q plays in piece P
% and 0 otherwise (indices are 0-based, as in the data).

slot(0..N-1) :- num_pieces(N).
piece(0..N-1) :- num_pieces(N).
player(0..M-1) :- num_players(M).

% each slot holds exactly one piece
1 { rehearsal_order(I,P) : piece(P) } 1 :- slot(I).

% each piece is rehearsed in exactly one slot
1 { rehearsal_order(I,P) : slot(I) } 1 :- piece(P).

% a player plays in the slot whose piece they are involved in
plays(Q,I) :- rehearsal_order(I,P), rehearsal(Q,P,1), player(Q).

% a player is present from the first slot in which they play until the last slot in which they play
present(Q,I) :- plays(Q,J), plays(Q,K), J <= I, I <= K, slot(I), player(Q).

% a player waits in every slot where they are present but not playing
waiting(Q,I) :- present(Q,I), not plays(Q,I).

% minimize the total time the players spend waiting: a waiting player waits for the length of the piece in that slot
#minimize { D,Q,I : waiting(Q,I), rehearsal_order(I,P), duration(P,D) }.

#show rehearsal_order/2.

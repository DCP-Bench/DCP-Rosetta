% csplib_039_rehearsal: a MiniZinc model from DCP Rosetta.
%
% A concert is to consist of a number of pieces of music of different durations, each involving a
% different combination of the members of the orchestra. Players can arrive at rehearsals immediately
% before the first piece in which they are involved and depart immediately after the last piece in which
% they are involved. The problem is to devise an order in which the pieces can be rehearsed so as to
% minimize the total time that players are waiting to play, i.e. the total time when players are present
% but not currently playing.
%
% Save this file as model.mzn. Download `csplib_039_rehearsal.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_039_rehearsal.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py csplib_039_rehearsal.json
%   minizinc model.mzn csplib_039_rehearsal_1.json

include "globals.mzn";

int: num_pieces;                                 % the number of pieces
int: num_players;                                 % the number of players in the orchestra
set of int: Pieces = 1..num_pieces;               % pieces, numbered from 1 (the output numbers them from 0)
set of int: Players = 1..num_players;             % the players
array[Pieces] of int: duration;                   % duration[j]: rehearsal time of piece j
array[Players, Pieces] of int: rehearsal;         % rehearsal[p,j] = 1 if player p plays in piece j

% plays[p]: player p is involved in at least one piece
array[Players] of bool: plays = [exists(j in Pieces)(rehearsal[p, j] = 1) | p in Players];

array[Pieces] of var Pieces: piece_at;            % piece_at[i]: the piece rehearsed in slot i
array[Pieces] of var Pieces: slot_of;             % slot_of[j]: the slot in which piece j is rehearsed
array[Players] of var Pieces: arrival;            % arrival[p]: first slot in which player p is present
array[Players] of var Pieces: departure;          % departure[p]: last slot in which player p is present

% each piece is rehearsed exactly once, and slot_of is its inverse
constraint all_different(piece_at);
constraint inverse(piece_at, slot_of);

% a player is present in every slot from arrival to departure, which covers each piece they play
constraint forall(p in Players, j in Pieces where rehearsal[p, j] = 1)
    (arrival[p] <= slot_of[j] /\ slot_of[j] <= departure[p]);

% the total time players are present but not playing
var int: objective = sum(p in Players, i in Pieces)(
    duration[piece_at[i]] * bool2int(plays[p] /\ arrival[p] <= i /\ i <= departure[p]
                                     /\ rehearsal[p, piece_at[i]] = 0));

solve minimize objective;
output ["{\"rehearsal_order\": ", showJSON([j - 1 | j in piece_at]), "}"];

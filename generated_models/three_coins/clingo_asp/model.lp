% three_coins: a clingo model from DCP Rosetta.
%
% Three coins lie on a table in the order tails, heads, tails. In precisely three moves make them face either all heads
% or all tails. Each move consists of choosing one coin and flipping it over. A face is 1 for tails and 0 for heads.
%
% Save this file as model.lp. Download `three_coins.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/three_coins.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py three_coins.json
%   python -m clingo model.lp three_coins_1.lp
%
% Input: num_moves(K) holds the number K of moves; init(J, V) holds the starting face V of coin J (0-based, as in
% the data; 1 for tails, 0 for heads).

face(0..1).
coin(J) :- init(J, _).
move(1..K) :- num_moves(K).

% the first configuration is the starting one
steps(0, J, V) :- init(J, V).

% after each move every coin shows one face
1 { steps(M, J, F) : face(F) } 1 :- move(M), coin(J).

% each move flips exactly one coin
flipped(M, J) :- move(M), coin(J), steps(M, J, F), steps(M - 1, J, G), F != G.
:- move(M), #count { J : flipped(M, J) } != 1.

% the final configuration has all coins showing heads or all coins showing tails
:- num_moves(K), #count { J : steps(K, J, 1) } > 0, #count { J : steps(K, J, 0) } > 0.

#show steps/3.

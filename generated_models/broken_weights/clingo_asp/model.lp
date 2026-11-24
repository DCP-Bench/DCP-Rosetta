% broken_weights: a clingo model from DCP Rosetta.
%
% A merchant had a measuring weight that broke into a number of pieces as the result of a fall. When the pieces were subsequently weighed, it was found that the weight of each piece was a whole number of pounds and that the pieces could be used to weigh every integral weight between 1 and the total weight. What were the weights of the pieces?
%
% Note that since this was a 17th-century merchant, he of course used a balance scale to weigh things. So, for example, he could use a 1-pound weight and a 4-pound weight to weigh a 3-pound object, by placing the 3-pound object and 1-pound weight on one side of the scale, and the 4-pound weight on the other side.
%
% Save this file as model.lp. Download `broken_weights.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py broken_weights.json
%   python -m clingo model.lp broken_weights_1.lp

% Input: m(M) holds the total weight M of the measuring weight, in pounds; n(N) holds the number N of pieces (the pieces are numbered 0 to N-1).

piece(0..N-1) :- n(N).
pound(1..M) :- m(M).

% each piece weighs a whole number of pounds from 1 to the total weight
1 { weights(I, W) : pound(W) } 1 :- piece(I).

% the pieces add up to the total weight
:- m(M), #sum { W, I : weights(I, W) } != M.

% reach(I, S): the first I pieces can give the net weight S on the scale. A piece on the other side of the object
% adds its weight, a piece on the object's side takes it away, and a piece that is not used adds nothing.
reach(0, 0) :- n(_).
reach(I+1, S) :- piece(I), reach(I, T), weights(I, W), S = T + W.
reach(I+1, S) :- piece(I), reach(I, T), weights(I, W), S = T - W.
reach(I+1, T) :- piece(I), reach(I, T).

% every whole number of pounds from 1 to the total weight can be weighed
:- n(N), pound(K), not reach(N, K).

#show weights/2.

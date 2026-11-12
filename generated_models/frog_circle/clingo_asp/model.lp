% frog_circle: a clingo model from DCP Rosetta.
%
% Cards numbered 1 to n are arranged in a circle. A frog jumps on card 1, then jumps to the card 1 place
% clockwise around the circle. Then, from card k, it jumps directly to the card k places clockwise around
% the circle. The frog continues jumping in this way forever. Find an arrangement of cards that allows the
% frog to jump on every card starting from card 1.
%
% Save this file as model.lp. Download `frog_circle.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py frog_circle.json
%   python -m clingo model.lp frog_circle_1.lp
%
% Input: n(N) holds the number N of cards.

% the positions around the circle are 0 to n-1, and the cards are 1 to n
position(0..N-1) :- n(N).
card(1..N) :- n(N).

% x(P, V): the card at position P around the circle is V; each position holds one card, and each card
% is used once
1 { x(P, V) : card(V) } 1 :- position(P).
1 { x(P, V) : position(P) } 1 :- card(V).

% symmetry breaking: turning the circle does not change the arrangement, so the list is written from card 1, where the frog starts: card 1 is at position 0
:- not x(0, 1).

% visit(I, P): the frog is on position P after I jumps; each jump moves it clockwise by the number on
% the card it is on, counted around the circle
visit(0, 0).
visit(I + 1, (P + V) \ N) :- visit(I, P), x(P, V), n(N), I + 1 < N.

% the frog lands on every card, so its positions after the jumps are all different
:- visit(I, P), visit(J, P), I < J.

#show x/2.

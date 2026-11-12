% csplib_015_schurs_lemma: a clingo model from DCP Rosetta.
%
% Put n balls labelled 1, ..., n into 3 boxes so that for any triple of balls x, y, z with x + y = z (where x and y
% may be equal), not all three are in the same box.
%
% Save this file as model.lp. Download `csplib_015_schurs_lemma.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py csplib_015_schurs_lemma.json
%   python -m clingo model.lp csplib_015_schurs_lemma_1.lp
%
% Input: n(N): the number N of balls; c(C): the number C of boxes. The balls are 1 to N and the boxes 1 to C.

ball(1..N) :- n(N).
box(1..C) :- c(C).

% box_of(X,B): ball X is in box B; each ball is in exactly one box
1 { box_of(X,B) : box(B) } 1 :- ball(X).

% for any x, y, z = x + y, the balls are not all in the same box
:- ball(X), ball(Y), ball(Z), Z = X + Y, box(B), box_of(X,B), box_of(Y,B), box_of(Z,B).

% balls(I,B): ball I + 1 is in box B, with I counted from 0
balls(X-1,B) :- box_of(X,B).

#show balls/2.

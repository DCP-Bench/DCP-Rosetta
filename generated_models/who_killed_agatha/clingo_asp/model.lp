% who_killed_agatha: a clingo model from DCP Rosetta.
%
% Someone in Dreadsbury Mansion killed Aunt Agatha. Agatha, the butler, and Charles live in Dreadsbury Mansion, and are
% the only ones to live there. A killer always hates, and is no richer than his victim. Charles hates no one that Agatha
% hates. Agatha hates everybody except the butler. The butler hates everyone not richer than Aunt Agatha. The butler
% hates everyone whom Agatha hates. No one hates everyone. Who killed Agatha?
%
% Save this file as model.lp. Download `who_killed_agatha.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/who_killed_agatha.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py who_killed_agatha.json
%   python -m clingo model.lp who_killed_agatha_1.lp
%
% Input: names(I, N) holds the name N of person I (0-based): "Agatha herself", "the butler" and "Charles".

person(I) :- names(I, _).
agatha(I) :- names(I, "Agatha herself").
butler(I) :- names(I, "the butler").
charles(I) :- names(I, "Charles").
people(N) :- N = #count { I : person(I) }.

% the killer is one of the people
1 { killer(K) : person(K) } 1.

% hates(X,Y): X hates Y. richer(X,Y): X is richer than Y.
{ hates(X, Y) : person(X), person(Y) }.
{ richer(X, Y) : person(X), person(Y) }.

% a killer always hates his victim
:- killer(K), agatha(A), not hates(K, A).

% a killer is no richer than his victim
:- killer(K), agatha(A), richer(K, A).

% richness: nobody is richer than himself, and of two different people exactly one is richer
:- richer(X, X).
:- person(X), person(Y), X < Y, richer(X, Y), richer(Y, X).
:- person(X), person(Y), X < Y, not richer(X, Y), not richer(Y, X).

% Charles hates no one that Agatha hates
:- charles(C), agatha(A), hates(C, X), hates(A, X).

% Agatha hates everybody except the butler
:- agatha(A), butler(B), hates(A, B).
:- agatha(A), person(X), not butler(X), not hates(A, X).

% the butler hates everyone not richer than Agatha
:- butler(B), agatha(A), person(X), not richer(X, A), not hates(B, X).

% the butler hates everyone whom Agatha hates
:- butler(B), agatha(A), hates(A, X), not hates(B, X).

% no one hates everyone
:- person(X), people(N), #count { Y : hates(X, Y) } >= N.

#show killer/1.

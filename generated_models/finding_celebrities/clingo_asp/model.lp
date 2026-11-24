% finding_celebrities: a clingo model from DCP Rosetta.
%
% Given a list of people at a party and for each person the list of people they know at the party, find the celebrities at the party. A celebrity is a person that everybody at the party knows but that only knows other celebrities. At least one celebrity is present at the party.
%
% Save this file as model.lp. Download `finding_celebrities.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/finding_celebrities.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py finding_celebrities.json
%   python -m clingo model.lp finding_celebrities_1.lp

% Input: graph(I, J, V) holds V, which is 1 when person I knows person J and 0 when not (indices 0-based).

% the people are those that have a row of the graph
person(I) :- graph(I, _, _).

% person P knows person Q (Q other than P)
knows(P, Q) :- graph(P, Q, 1), P != Q.

% each person is a celebrity (c(P)) or not; at least one is a celebrity
1 { c(P) : person(P) }.

% unknown(P): some other person does not know P, so P is not known by everybody
unknown(P) :- person(P), person(Q), P != Q, not knows(Q, P).

% a person knows someone who is not a celebrity
knows_other_guest(P) :- knows(P, Q), not c(Q).

% a celebrity is a person that everybody knows and who knows only other celebrities
celebrity(P) :- person(P), not unknown(P), not knows_other_guest(P).

% the celebrities are exactly those that are known by everybody and know only celebrities
:- c(P), not celebrity(P).
:- celebrity(P), not c(P).

% the output: each person as true (a celebrity) or false
celebrities(P, true) :- c(P).
celebrities(P, false) :- person(P), not c(P).

#show celebrities/2.

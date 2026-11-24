% session3_kidney_exchange: a clingo model from DCP Rosetta.
%
% At the hospital n people are on a waiting list for a kidney's transplant. We have the information about the compatibility between these people as a directed graph: compatible[i] is the set of people to which i can donate. Given this information, we want to maximize the number of people that receive a new kidney: anyone who gives a kidney must receive one, and no person receives more than one kidney.
%
% Save this file as model.lp. Download `session3_kidney_exchange.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_kidney_exchange.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py session3_kidney_exchange.json
%   python -m clingo model.lp session3_kidney_exchange_1.lp
%
% Input: num_people(N) holds the number N of people; compatible(I, K, P) holds that the K-th entry of the list
% of person I is person P, to whom I can donate (I and K are 0-based; P is numbered from 1, as in the data).

person(0..N-1) :- num_people(N).

% a person can donate to the people listed for him, shifted to 0-based numbers
can_donate(I, P - 1) :- compatible(I, _, P).

% each person gives at most one kidney, to one person he can donate to
{ donates(I, J) : can_donate(I, J) } 1 :- person(I).

% no person receives more than one kidney
receives(J) :- donates(_, J).
:- person(J), #count { I : donates(I, J) } > 1.

% anyone who gives a kidney must receive one
:- donates(I, _), not receives(I).

% maximize the number of people that receive a kidney
#maximize { 1, J : receives(J) }.

% the output: true when person I donates to person J, false otherwise
transplants(I, J, true)  :- donates(I, J).
transplants(I, J, false) :- person(I), person(J), not donates(I, J).

#show transplants/3.

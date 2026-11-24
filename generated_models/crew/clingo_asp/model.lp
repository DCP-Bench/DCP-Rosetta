% crew: a clingo model from DCP Rosetta.
%
% Assign flight attendants to flights. Each flight needs a certain number of cabin crew, and they have to speak
% certain languages. A flight has exactly the required number of cabin crew, and at least the required number of
% stewards, hostesses, French speakers, Spanish speakers and German speakers; one person can count towards several
% of them. Every cabin crew member has at least two flights off after an attended flight, so nobody attends more
% than one of any three consecutive flights.
%
% Save this file as model.lp. Download `crew.json` and `dcp_convert_asp.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
% Convert the instances once, then run the first one (clingo 5.8, e.g. `pip install clingo`):
%   python dcp_convert_asp.py crew.json
%   python -m clingo model.lp crew_1.lp
%
% Input: attributes(P, K, V) holds the value V (0 or 1) of person P for attribute K, where K = 0 is steward,
% 1 hostess, 2 French, 3 Spanish, 4 German; required_crew(F, K, N) holds the number N for flight F, where K = 0 is
% the number of cabin crew and K = 1 to 5 are the numbers of stewards, hostesses, French, Spanish and German
% speakers needed (indices are 0-based, as in the data).

person(P) :- attributes(P,_,_).
flight(F) :- required_crew(F,_,_).

% skill(P, K): person P has the skill K, where K = 1 is steward, 2 hostess, 3 French, 4 Spanish, 5 German
skill(P,K) :- attributes(P,J,1), K = J+1.

% each person is either assigned to a flight or not
{ assigned(F,P) } :- flight(F), person(P).

% each flight has exactly the required number of cabin crew
:- flight(F), required_crew(F,0,N), #count { P : assigned(F,P) } != N.

% each flight has at least the required number of stewards, hostesses, French, Spanish and German speakers
:- flight(F), required_crew(F,K,N), K > 0, #count { P : assigned(F,P), skill(P,K) } < N.

% nobody attends two flights within any three consecutive flights
:- assigned(F,P), assigned(G,P), F < G, G - F <= 2.

% crew(F,P,true) when person P is assigned to flight F, crew(F,P,false) when not
crew(F,P,true) :- assigned(F,P).
crew(F,P,false) :- flight(F), person(P), not assigned(F,P).

#show crew/3.

% session1_thick_as_thieves: a clingo model from DCP Rosetta.
%
% Following a robbery at Sparkles the Jeweller's, Inspector Korner of the Yard interviewed six of the usual suspects. He knew that the getaway car had been barely big enough to hold two, so he reckoned that at least four of them were innocent - but which ones? He also supposed that the innocent ones would tell the truth, while the guilty one or ones would lie. What they actually said was: ARTIE: "It wasn't me." BILL: "Crackitt was in it up to his neck." CRACKITT: "No I wasn't." DODGY: "If Crackitt did it, Bill did it with him." EDGY: "Nobody did it alone." FINGERS: "That's right: it was Artie and Dodgy together." If the good inspector's suppositions were correct, who is guilty?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

suspect(artie). suspect(bill). suspect(crackitt).
suspect(dodgy). suspect(edgy). suspect(fingers).

% each suspect is either guilty (true) or innocent (false)
1 { artie(true); artie(false) } 1.
1 { bill(true); bill(false) } 1.
1 { crackitt(true); crackitt(false) } 1.
1 { dodgy(true); dodgy(false) } 1.
1 { edgy(true); edgy(false) } 1.
1 { fingers(true); fingers(false) } 1.

guilty(artie) :- artie(true).
guilty(bill) :- bill(true).
guilty(crackitt) :- crackitt(true).
guilty(dodgy) :- dodgy(true).
guilty(edgy) :- edgy(true).
guilty(fingers) :- fingers(true).

% the number of guilty suspects
guilty_count(K) :- K = #count { P : guilty(P) }.

% the getaway car was barely big enough to hold two, so at most two are guilty
:- guilty_count(K), K > 2.

% says_true(P) holds when the statement of suspect P is true
% ARTIE: "It wasn't me."
says_true(artie) :- not guilty(artie).
% BILL: "Crackitt was in it up to his neck."
says_true(bill) :- guilty(crackitt).
% CRACKITT: "No I wasn't."
says_true(crackitt) :- not guilty(crackitt).
% DODGY: "If Crackitt did it, Bill did it with him."
says_true(dodgy) :- not guilty(crackitt).
says_true(dodgy) :- guilty(bill).
% EDGY: "Nobody did it alone." (false only when exactly one is guilty)
says_true(edgy) :- guilty_count(K), K != 1.
% FINGERS: "It was Artie and Dodgy together."
says_true(fingers) :- guilty(artie), guilty(dodgy), guilty_count(2).

% the guilty ones lie
:- guilty(P), says_true(P).

% the innocent ones tell the truth
:- suspect(P), not guilty(P), not says_true(P).

#show artie/1.
#show bill/1.
#show crackitt/1.
#show dodgy/1.
#show edgy/1.
#show fingers/1.

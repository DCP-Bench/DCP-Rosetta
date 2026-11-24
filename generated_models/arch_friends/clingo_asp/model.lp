% arch_friends: a clingo model from DCP Rosetta.
%
% Harriet, upon returning from the mall, is happily describing her four shoe purchases to her friend Aurora. Aurora just loves the four different kinds of shoes that Harriet bought (ecru espadrilles, fuchsia flats, purple pumps, and suede sandals), but Harriet can't recall at which different store (Foot Farm, Heels in a Handcart, The Shoe Palace, or Tootsies) she got each pair. Can you help these two figure out the order in which Harriet bought each pair of shoes, and where she bought each? Harriet bought fuchsia flats at Heels in a Handcart. The store she visited just after buying her purple pumps was not Tootsies. The Foot Farm was Harriet's second stop. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
% Save this file as model.lp and run it (clingo 5.8, e.g. `pip install clingo`) with:
%   python -m clingo model.lp

% The stops are numbered 1 to 4.
stop(1..4).

% each shoe is bought at exactly one stop, and each stop is one shoe purchase
1 { ecruespadrilles(S) : stop(S) } 1.
1 { fuchsiaflats(S) : stop(S) } 1.
1 { purplepumps(S) : stop(S) } 1.
1 { suedesandals(S) : stop(S) } 1.
shoe(ecru,S) :- ecruespadrilles(S).
shoe(fuchsia,S) :- fuchsiaflats(S).
shoe(purple,S) :- purplepumps(S).
shoe(suede,S) :- suedesandals(S).
:- stop(S), #count { X : shoe(X,S) } != 1.

% each store is visited at exactly one stop, and each stop is one store visit
1 { footfarm(S) : stop(S) } 1.
1 { heelsinahandcart(S) : stop(S) } 1.
1 { theshoepalace(S) : stop(S) } 1.
1 { tootsies(S) : stop(S) } 1.
store(farm,S) :- footfarm(S).
store(heels,S) :- heelsinahandcart(S).
store(palace,S) :- theshoepalace(S).
store(toots,S) :- tootsies(S).
:- stop(S), #count { X : store(X,S) } != 1.

% Harriet bought fuchsia flats at Heels in a Handcart: the fuchsia flats and Heels are at the same stop
:- fuchsiaflats(S), not heelsinahandcart(S).

% the store visited just after buying the purple pumps was not Tootsies
:- purplepumps(S), tootsies(S+1).

% the Foot Farm was the second stop
:- not footfarm(2).

% the suede sandals were bought two stops after leaving The Shoe Palace
:- theshoepalace(S), not suedesandals(S+2).

#show ecruespadrilles/1.
#show fuchsiaflats/1.
#show purplepumps/1.
#show suedesandals/1.
#show footfarm/1.
#show heelsinahandcart/1.
#show theshoepalace/1.
#show tootsies/1.

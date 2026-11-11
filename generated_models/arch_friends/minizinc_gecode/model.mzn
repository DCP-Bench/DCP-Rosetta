% arch_friends: a MiniZinc model from DCP Rosetta.
%
% Harriet, upon returning from the mall, is happily describing her four shoe purchases to her friend
% Aurora. Aurora just loves the four different kinds of shoes that Harriet bought (ecru espadrilles,
% fuchsia flats, purple pumps, and suede sandals), but Harriet can't recall at which different store (Foot
% Farm, Heels in a Handcart, The Shoe Palace, or Tootsies) she got each pair. Help these two figure out the
% order in which Harriet bought each pair of shoes, and where she bought each.
%
% 1. Harriet bought fuchsia flats at Heels in a Handcart.
% 2. The store she visited just after buying her purple pumps was not Tootsies.
% 3. The Foot Farm was Harriet's second stop.
% 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

% the stops, numbered in the order Harriet visited them
set of int: Stops = 1..4;

% each variable is the stop at which that shoe was bought
var Stops: ecruespadrilles;
var Stops: fuchsiaflats;
var Stops: purplepumps;
var Stops: suedesandals;

% each variable is the stop at which that store was visited
var Stops: footfarm;
var Stops: heelsinahandcart;
var Stops: theshoepalace;
var Stops: tootsies;

% each stop is one shoe purchase
constraint all_different([ecruespadrilles, fuchsiaflats, purplepumps, suedesandals]);

% each stop is one store visit
constraint all_different([footfarm, heelsinahandcart, theshoepalace, tootsies]);

% Harriet bought fuchsia flats at Heels in a Handcart
constraint fuchsiaflats = heelsinahandcart;

% the store visited just after the purple pumps was not Tootsies
constraint purplepumps + 1 != tootsies;

% the Foot Farm was the second stop
constraint footfarm = 2;

% two stops after leaving The Shoe Palace, she bought the suede sandals
constraint suedesandals = theshoepalace + 2;

solve satisfy;

output ["{\"ecruespadrilles\": ", showJSON(ecruespadrilles),
        ", \"footfarm\": ", showJSON(footfarm),
        ", \"fuchsiaflats\": ", showJSON(fuchsiaflats),
        ", \"heelsinahandcart\": ", showJSON(heelsinahandcart),
        ", \"purplepumps\": ", showJSON(purplepumps),
        ", \"suedesandals\": ", showJSON(suedesandals),
        ", \"theshoepalace\": ", showJSON(theshoepalace),
        ", \"tootsies\": ", showJSON(tootsies), "}"];

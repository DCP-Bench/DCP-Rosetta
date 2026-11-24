% handshaking: a MiniZinc model from DCP Rosetta.
%
% Hilary and Jocelyn are married. They invite a number of couples who are friends for dinner. When they
% arrive, they shake hands with each other. Nobody shakes hands with him or herself or with his or her
% spouse. After there has been some handshaking, Jocelyn jumps up on a chair and says 'Stop shaking
% hands!', and then asks how many hands each person has shaken. All the answers are different. How
% many hands has Hilary shaken?
%
% Save this file as model.mzn. Download `handshaking.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/handshaking.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py handshaking.json
%   minizinc model.mzn handshaking_1.json

include "globals.mzn";

int: num_couples;                          % the couples invited, not counting Hilary and Jocelyn
int: n = 2 + 2 * num_couples;              % all people at the dinner
set of int: People = 1..n;

int: Hilary = 1;
int: Jocelyn = 2;

% the spouse of person p: Hilary and Jocelyn are married to each other, and the invited couples are
% the pairs (3,4), (5,6), ...
function int: spouse(int: p) =
    if p <= 2 then 3 - p
    elseif p mod 2 = 1 then p + 1
    else p - 1 endif;

% y[i,j]: person i shakes hands with person j
array[People, People] of var bool: y;

% x[i]: the number of hands person i has shaken; nobody shakes his or her own hand or the hand of the
% spouse, so at most n - 2 hands
array[People] of var 0..n - 2: x;

% the number of hands Hilary has shaken
var 0..n - 2: hil = x[Hilary];

% nobody shakes hands with him or herself
constraint forall(i in People)(not y[i,i]);

% nobody shakes hands with his or her spouse
constraint forall(i in People)(not y[i, spouse(i)]);

% a handshake is between two people: i shakes hands with j exactly when j shakes hands with i
constraint forall(i, j in People where i < j)(y[i,j] = y[j,i]);

% x[i] counts the handshakes of person i
constraint forall(i in People)(x[i] = sum(j in People)(bool2int(y[i,j])));

% all the answers are different: Jocelyn asks everyone else how many hands they have shaken
constraint all_different([x[i] | i in People where i != Jocelyn]);

% Symmetry breaking, which keeps one of each situation: swapping the two spouses of an invited couple,
% or swapping two invited couples, leaves Hilary's count unchanged. So the answers of each invited couple
% are in increasing order, and the couples are in increasing order of their first spouse's answer.
constraint forall(c in 1..num_couples)(x[2 * c + 1] < x[2 * c + 2]);
constraint forall(c in 1..num_couples - 1)(x[2 * c + 1] < x[2 * c + 3]);

solve satisfy;

output ["{\"hil\": ", showJSON(hil), "}"];

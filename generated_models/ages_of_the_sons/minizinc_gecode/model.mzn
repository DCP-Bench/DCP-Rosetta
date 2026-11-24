% ages_of_the_sons: a MiniZinc model from DCP Rosetta.
%
% An old man asked a mathematician to guess the ages of his three sons. The old man said: "The product of
% their ages is 36." The mathematician said: "I need more information." The old man said: "Over there you
% can see a building. The sum of their ages equals the number of the windows in that building." After a
% short while the mathematician said: "I need more information." The old man said: "The oldest son has
% blue eyes." The mathematician said: "I got it." What are the ages of the three sons of the old man?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

% the ages are positive whole numbers; with a product of 36 no age can exceed 36
set of int: Ages = 1..36;

% cand[a,b,c]: (a,b,c) is a candidate triple of ages, oldest first, whose product is 36
array[Ages, Ages, Ages] of bool: cand =
    array3d(Ages, Ages, Ages, [a >= b /\ b >= c /\ a * b * c = 36 | a in Ages, b in Ages, c in Ages]);
% total[a,b,c]: the sum of the ages in the triple (a,b,c)
array[Ages, Ages, Ages] of int: total =
    array3d(Ages, Ages, Ages, [a + b + c | a in Ages, b in Ages, c in Ages]);

var Ages: A1;                                  % the oldest son
var Ages: A2;                                  % the middle son
var Ages: A3;                                  % the youngest son

% the product of the three ages is 36
constraint A1 * A2 * A3 = 36;

% the ages are listed oldest first
constraint A1 >= A2 /\ A2 >= A3;

% the product alone does not tell the mathematician the ages: another candidate triple has the product 36
constraint exists(a in Ages, b in Ages, c in Ages)(cand[a,b,c] /\ (a != A1 \/ b != A2 \/ c != A3));

% the sum alone does not tell the mathematician the ages: another candidate triple with the product 36
% has the same sum as the sons' ages
constraint exists(a in Ages, b in Ages, c in Ages)(
    cand[a,b,c] /\ total[a,b,c] = A1 + A2 + A3 /\ (a != A1 \/ b != A2 \/ c != A3));

% the oldest son is identified, so he is strictly older than the middle son
constraint A1 > A2;

% knowing the oldest son is the unique oldest, the mathematician can tell the ages: among the candidate
% triples with the product 36 and the same sum, only the true triple has a unique oldest son
constraint forall(a in Ages, b in Ages, c in Ages)(
    (cand[a,b,c] /\ total[a,b,c] = A1 + A2 + A3 /\ a > b) -> (a = A1 /\ b = A2 /\ c = A3));

solve satisfy;

output ["{\"A1\": ", showJSON(A1), ", \"A2\": ", showJSON(A2), ", \"A3\": ", showJSON(A3), "}"];

% session1_thick_as_thieves: a MiniZinc model from DCP Rosetta.
%
% Following a robbery at Sparkles the Jeweller's, Inspector Korner of the Yard interviewed six of the usual suspects. He
% knew that the getaway car had been barely big enough to hold two, so he reckoned that at least four of them were
% innocent - but which ones? He also supposed that the innocent ones would tell the truth, while the guilty one or ones
% would lie. What they actually said was:
% - ARTIE: "It wasn't me."
% - BILL: "Crackitt was in it up to his neck."
% - CRACKITT: "No I wasn't."
% - DODGY: "If Crackitt did it, Bill did it with him."
% - EDGY: "Nobody did it alone."
% - FINGERS: "That's right: it was Artie and Dodgy together."
% If the good inspector's suppositions were correct, who is guilty?
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

var bool: artie;      % Artie is guilty
var bool: bill;       % Bill is guilty
var bool: crackitt;   % Crackitt is guilty
var bool: dodgy;      % Dodgy is guilty
var bool: edgy;       % Edgy is guilty
var bool: fingers;    % Fingers is guilty

var 0..6: num_guilty = bool2int(artie) + bool2int(bill) + bool2int(crackitt)
                     + bool2int(dodgy) + bool2int(edgy) + bool2int(fingers);

% the getaway car could hold only two, so at least four of them are innocent
constraint num_guilty <= 2;

% the innocent ones tell the truth and the guilty ones lie: Artie's words are true exactly when he is innocent
constraint (not artie) <-> (not artie);

% Bill's words ("Crackitt was in it up to his neck") are true exactly when Bill is innocent
constraint (not bill) <-> crackitt;

% Crackitt's words ("No I wasn't") are true exactly when Crackitt is innocent
constraint (not crackitt) <-> (not crackitt);

% Dodgy's words ("If Crackitt did it, Bill did it with him") are true exactly when Dodgy is innocent
constraint (not dodgy) <-> (crackitt -> bill);

% Edgy's words ("Nobody did it alone") are true exactly when Edgy is innocent
constraint (not edgy) <-> (num_guilty != 1);

% Fingers' words ("it was Artie and Dodgy together") are true exactly when Fingers is innocent
constraint (not fingers) <-> (artie /\ dodgy /\ num_guilty = 2);

solve satisfy;
output ["{\"artie\": ", showJSON(artie), ", \"bill\": ", showJSON(bill), ", \"crackitt\": ", showJSON(crackitt),
        ", \"dodgy\": ", showJSON(dodgy), ", \"edgy\": ", showJSON(edgy), ", \"fingers\": ", showJSON(fingers), "}"];

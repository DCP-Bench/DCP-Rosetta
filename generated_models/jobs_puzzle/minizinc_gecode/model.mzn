% jobs_puzzle: a MiniZinc model from DCP Rosetta.
%
% Four people hold eight different jobs: chef, guard, nurse, clerk, police officer, teacher, actor and
% boxer. Each person holds exactly two jobs. Clues:
%   1. The nurse is not a teacher, police officer, or clerk.
%   2. The clerk is not the chef.
%   3. Person 0 is not the boxer.
%   4. Person 3 is not the teacher, police officer, or nurse.
%   5. Person 0, the chef, and the police officer went golfing together.
% Determine which person holds which two jobs.
%
%   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
% Save this file as model.mzn and run it (MiniZinc 2.8 or later) with:
%   minizinc model.mzn

include "globals.mzn";

set of int: Persons = 0..3;                      % the four people, numbered 0 to 3
set of int: Jobs = 1..8;                         % the eight jobs

% each variable is the person holding that job
var Persons: chef;
var Persons: guard;
var Persons: nurse;
var Persons: clerk;
var Persons: police_officer;
var Persons: teacher;
var Persons: actor;
var Persons: boxer;

% holder[j]: the person holding job j, in the order chef, guard, nurse, clerk, police officer, teacher, actor, boxer
array[Jobs] of var Persons: holder = [chef, guard, nurse, clerk, police_officer, teacher, actor, boxer];

% each person holds exactly two jobs
constraint global_cardinality(holder, [p | p in Persons], [2 | p in Persons]);

% 1. the nurse is not a teacher, police officer or clerk
constraint nurse != teacher /\ nurse != police_officer /\ nurse != clerk;

% 2. the clerk is not the chef
constraint clerk != chef;

% 3. person 0 is not the boxer
constraint boxer != 0;

% 4. person 3 is not the teacher, police officer or nurse
constraint teacher != 3 /\ police_officer != 3 /\ nurse != 3;

% 5. person 0, the chef and the police officer are three different people
constraint all_different([0, chef, police_officer]);

solve satisfy;

output ["{\"chef\": ", showJSON(chef), ", \"guard\": ", showJSON(guard), ", \"nurse\": ", showJSON(nurse),
        ", \"clerk\": ", showJSON(clerk), ", \"police_officer\": ", showJSON(police_officer),
        ", \"teacher\": ", showJSON(teacher), ", \"actor\": ", showJSON(actor),
        ", \"boxer\": ", showJSON(boxer), "}"];

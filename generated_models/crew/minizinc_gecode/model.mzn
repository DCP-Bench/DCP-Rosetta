% crew: a MiniZinc model from DCP Rosetta.
%
% Assign flight attendants to flights. Each flight needs a certain number of cabin crew, and they have
% to speak certain languages. attributes[p] describes person p as five 0/1 values: steward, hostess,
% speaks French, speaks Spanish, speaks German. required_crew[f] describes flight f as six numbers: the
% number of cabin crew, then the numbers of stewards, hostesses, French speakers, Spanish speakers and
% German speakers needed. A flight has exactly that number of cabin crew, and at least the required
% number of each of the others; one person can count towards several of them. Every cabin crew member
% has at least two flights off after an attended flight, so nobody attends more than one of any three
% consecutive flights.
%
% Save this file as model.mzn. Download `crew.json` and `dcp_convert_mzn.py` from the
% problem's page:
%   https://dcp-bench.github.io/DCP-Rosetta/problems/crew.html
% Convert the instances once, then run the first one (MiniZinc 2.8 or later):
%   python dcp_convert_mzn.py crew.json
%   minizinc model.mzn crew_1.json

array[int, int] of int: attributes;     % attributes[p, k]: 1 if person p has attribute k, 0 otherwise
array[int, int] of int: required_crew;  % required_crew[f, 1]: cabin crew of flight f, [f, 2..6]: its requirements

set of int: Persons = index_set_1of2(attributes);      % one index per person
set of int: Flights = index_set_1of2(required_crew);   % one index per flight
set of int: Attributes = index_set_2of2(attributes);   % steward, hostess, French, Spanish, German

% crew[f, p]: person p is assigned to flight f
array[Flights, Persons] of var bool: crew;

% each flight has exactly the required number of cabin crew
constraint forall(f in Flights)(
    sum(p in Persons)(bool2int(crew[f, p])) = required_crew[f, 1]);

% each flight has at least the required number of crew with each attribute
constraint forall(f in Flights, k in Attributes)(
    sum(p in Persons)(attributes[p, k] * bool2int(crew[f, p])) >= required_crew[f, k + 1]);

% nobody is assigned to more than one of any three consecutive flights
constraint forall(p in Persons, f in min(Flights)..max(Flights) - 2)(
    sum(g in f..f + 2)(bool2int(crew[g, p])) <= 1);

solve satisfy;

output ["{\"crew\": ", showJSON(crew), "}"];

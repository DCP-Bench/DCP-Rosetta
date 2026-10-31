#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"

using namespace operations_research;
using namespace operations_research::sat;

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "usage: " << argv[0] << " INSTANCE.json\n";
    return 2;
  }
  std::ifstream in(argv[1]);
  const nlohmann::json instance = nlohmann::json::parse(in);
  const auto addends = instance.at("addends").get<std::vector<std::string>>();
  const std::string sum = instance.at("sum").get<std::string>();

  CpModelBuilder model;
  std::map<char, IntVar> digit;
  auto letter = [&](char c) -> IntVar& {
    auto it = digit.find(c);
    if (it == digit.end()) it = digit.emplace(c, model.NewIntVar(Domain(0, 9))).first;
    return it->second;
  };

  // Every word enters the sum as place value times digit; the leading digit of
  // a multi-letter word is non-zero.
  LinearExpr difference;
  auto add_word = [&](const std::string& word, int64_t sign) {
    int64_t place = 1;
    for (auto it = word.rbegin(); it != word.rend(); ++it) {
      IntVar& d = letter(*it);
      difference += (sign * place) * d;
      place *= 10;
    }
    if (word.size() > 1) model.AddGreaterOrEqual(letter(word[0]), 1);
  };
  for (const auto& word : addends) add_word(word, 1);
  add_word(sum, -1);
  model.AddEquality(difference, 0);

  std::vector<LinearExpr> all_digits;
  for (auto& [c, d] : digit) all_digits.push_back(LinearExpr(d));
  model.AddAllDifferent(all_digits);

  const CpSolverResponse response = Solve(model.Build());
  if (response.status() == CpSolverStatus::INFEASIBLE) {
    std::cout << "{\"status\": \"unsatisfiable\"}\n";
    return 0;
  }
  if (response.status() != CpSolverStatus::OPTIMAL &&
      response.status() != CpSolverStatus::FEASIBLE) {
    std::cerr << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
    return 1;
  }
  std::cout << "{\"digits\": {";
  bool first = true;
  for (auto& [c, d] : digit) {
    std::cout << (first ? "" : ", ") << "\"" << c << "\": "
              << SolutionIntegerValue(response, d);
    first = false;
  }
  std::cout << "}}\n";
  return 0;
}

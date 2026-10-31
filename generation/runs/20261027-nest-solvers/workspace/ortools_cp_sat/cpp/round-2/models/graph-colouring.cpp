#include <cstdint>
#include <fstream>
#include <iostream>
#include <utility>
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
  const int n = instance.at("n_nodes").get<int>();
  const auto edges = instance.at("edges").get<std::vector<std::pair<int, int>>>();

  CpModelBuilder model;
  std::vector<IntVar> colour;
  for (int i = 0; i < n; ++i) colour.push_back(model.NewIntVar(Domain(0, n - 1)));
  for (const auto& [a, b] : edges) model.AddNotEqual(colour[a], colour[b]);

  // The largest colour index; minimising it minimises the number of colours.
  const IntVar largest = model.NewIntVar(Domain(0, n - 1));
  std::vector<LinearExpr> exprs(colour.begin(), colour.end());
  model.AddMaxEquality(largest, exprs);
  model.Minimize(largest);

  const CpSolverResponse response = Solve(model.Build());
  if (response.status() != CpSolverStatus::OPTIMAL) {
    std::cerr << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
    return 1;
  }
  std::cout << "{\"colour\": [";
  for (int i = 0; i < n; ++i) {
    std::cout << (i ? ", " : "") << SolutionIntegerValue(response, colour[i]);
  }
  std::cout << "]}\n";
  return 0;
}

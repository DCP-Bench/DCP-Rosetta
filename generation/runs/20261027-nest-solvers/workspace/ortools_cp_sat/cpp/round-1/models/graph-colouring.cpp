// Graph colouring with the fewest colours. Minimise the largest colour index; at an
// optimum the colours used are 0..k-1, so the number of distinct colours is k.
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
  for (const auto& [u, v] : edges) model.AddNotEqual(colour[u], colour[v]);

  IntVar largest = model.NewIntVar(Domain(0, n - 1));
  const std::vector<LinearExpr> colour_exprs(colour.begin(), colour.end());
  model.AddMaxEquality(largest, colour_exprs);
  model.Minimize(largest);

  const CpSolverResponse response = Solve(model.Build());
  if (response.status() != CpSolverStatus::OPTIMAL) {
    std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
    return 1;
  }
  nlohmann::json out;
  out["colour"] = nlohmann::json::array();
  for (const IntVar& c : colour) out["colour"].push_back(SolutionIntegerValue(response, c));
  std::cout << out.dump() << "\n";
  return 0;
}

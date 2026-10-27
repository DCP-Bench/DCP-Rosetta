#include <cstdint>
#include <fstream>
#include <iostream>
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
  const int n = nlohmann::json::parse(in).at("n").get<int>();

  CpModelBuilder model;
  std::vector<IntVar> queens;
  for (int i = 0; i < n; ++i) queens.push_back(model.NewIntVar(Domain(0, n - 1)));

  std::vector<LinearExpr> cols(queens.begin(), queens.end());
  std::vector<LinearExpr> up;
  std::vector<LinearExpr> down;
  for (int i = 0; i < n; ++i) {
    up.push_back(LinearExpr(queens[i]) + int64_t(i));
    down.push_back(LinearExpr(queens[i]) - int64_t(i));
  }
  model.AddAllDifferent(cols);
  model.AddAllDifferent(up);
  model.AddAllDifferent(down);

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
  std::cout << "{\"queens\": [";
  for (int i = 0; i < n; ++i) {
    std::cout << (i ? ", " : "") << SolutionIntegerValue(response, queens[i]);
  }
  std::cout << "]}\n";
  return 0;
}

// N-queens: print every placement, one JSON object per line.
#include <cstdint>
#include <fstream>
#include <iostream>
#include <vector>

#include <nlohmann/json.hpp>

#include "ortools/sat/cp_model.h"
#include "ortools/sat/cp_model_solver.h"
#include "ortools/sat/model.h"
#include "ortools/sat/sat_parameters.pb.h"

using namespace operations_research;
using namespace operations_research::sat;

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "usage: " << argv[0] << " INSTANCE.json\n";
    return 2;
  }
  std::ifstream in(argv[1]);
  const nlohmann::json instance = nlohmann::json::parse(in);
  const int n = instance.at("n").get<int>();

  CpModelBuilder model;
  std::vector<IntVar> queens;
  for (int row = 0; row < n; ++row) queens.push_back(model.NewIntVar(Domain(0, n - 1)));

  const std::vector<LinearExpr> columns(queens.begin(), queens.end());
  std::vector<LinearExpr> up_diagonals;
  std::vector<LinearExpr> down_diagonals;
  for (int row = 0; row < n; ++row) {
    up_diagonals.push_back(LinearExpr(queens[row]) + static_cast<int64_t>(row));
    down_diagonals.push_back(LinearExpr(queens[row]) - static_cast<int64_t>(row));
  }
  model.AddAllDifferent(columns);
  model.AddAllDifferent(up_diagonals);
  model.AddAllDifferent(down_diagonals);

  Model enumerator;
  enumerator.Add(NewFeasibleSolutionObserver([&](const CpSolverResponse& r) {
    nlohmann::json out;
    out["queens"] = nlohmann::json::array();
    for (const IntVar& q : queens) out["queens"].push_back(SolutionIntegerValue(r, q));
    std::cout << out.dump() << "\n";
  }));
  SatParameters parameters;
  parameters.set_enumerate_all_solutions(true);
  parameters.set_num_workers(1);
  enumerator.Add(NewSatParameters(parameters));
  const CpSolverResponse response = SolveCpModel(model.Build(), &enumerator);
  std::cout << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
  return 0;
}

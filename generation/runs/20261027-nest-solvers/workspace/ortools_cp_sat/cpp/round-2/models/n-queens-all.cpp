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

  Model enumerator;
  int count = 0;
  enumerator.Add(NewFeasibleSolutionObserver([&](const CpSolverResponse& r) {
    ++count;
    std::cout << "{\"queens\": [";
    for (int i = 0; i < n; ++i) {
      std::cout << (i ? ", " : "") << SolutionIntegerValue(r, queens[i]);
    }
    std::cout << "]}\n";
  }));
  SatParameters parameters;
  parameters.set_enumerate_all_solutions(true);
  parameters.set_num_workers(1);
  enumerator.Add(NewSatParameters(parameters));

  const CpSolverResponse response = SolveCpModel(model.Build(), &enumerator);
  if (count == 0 && response.status() == CpSolverStatus::INFEASIBLE) {
    std::cout << "{\"status\": \"unsatisfiable\"}\n";
    return 0;
  }
  if (response.status() != CpSolverStatus::OPTIMAL) {
    std::cerr << "Status: " << CpSolverStatus_Name(response.status()) << "\n";
    return 1;
  }
  return 0;
}

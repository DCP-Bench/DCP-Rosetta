cmake_minimum_required(VERSION 3.18)
project(models LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(ortools CONFIG REQUIRED)
find_package(nlohmann_json CONFIG REQUIRED)

set(PROGRAMS cryptarithm graph-colouring jobshop knapsack knapsack-all-optimal n-queens n-queens-all)
foreach(program IN LISTS PROGRAMS)
  add_executable(${program} models/${program}.cpp)
  target_link_libraries(${program} PRIVATE ortools::ortools nlohmann_json::nlohmann_json)
  set_target_properties(${program} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
endforeach()

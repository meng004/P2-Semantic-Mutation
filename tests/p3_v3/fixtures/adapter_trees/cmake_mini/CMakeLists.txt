cmake_minimum_required(VERSION 3.16)
project(cmake_mini LANGUAGES C CXX CUDA Fortran)

enable_testing()
add_test(mini_smoke mini_tool --smoke)
add_test(NAME mini_named COMMAND mini_tool --named)
add_executable(mini_tool src/lib.c)

add_subdirectory(examples)

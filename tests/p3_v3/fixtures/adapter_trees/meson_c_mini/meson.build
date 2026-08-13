project('meson-c-mini', 'c')

mtool = executable('mtool', 'src/m.c')
test('t1', mtool)
benchmark('b1', mtool)
custom_test('phantom-test', mtool)
foo_benchmark('phantom-benchmark', mtool)
foo_executable('phantom-tool', 'src/m.c')

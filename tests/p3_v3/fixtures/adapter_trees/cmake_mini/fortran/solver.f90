subroutine mini_solve(value)
  integer :: value
  value = value + 1
end subroutine mini_solve

integer function mini_energy(value)
  integer :: value
  mini_energy = value * value
end function mini_energy

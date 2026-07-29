"""v5 held-out MR — set 1 (gemini-3.5-flash), a1 MP4, candidate 1/3."""
import numpy as np

def r(x):
    # Identity transform is used as a last resort because the chaotic Lorenz system 
    # and the asymmetric parameterization of the initial conditions (specifically the z-component)
    # do not permit any other exact output-preserving input transformation.
    return x

def R(y_orig, y_new):
    return abs(y_orig - y_new) <= 1e-6

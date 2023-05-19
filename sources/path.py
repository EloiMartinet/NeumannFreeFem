#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import os
import sys

# Parameters of the mesh
HMESH = 0.01  # Size of a mesh element

# Other parameters
EPS           = 1e-2    # The non-degeneracy parameter
ALPHA         = 0.01    # Parameter for velocity extension - regularization
MAXIT         = 200     # Maximum number of iterations in the shape optimization process
MAXITLS       = 10      # Maximum number of iterations in the line search procedure
MAXCOEF       = 20.0    # Maximum allowed move between two iterations (in # * STEP)
MINCOEF       = 0.002   # Minimum allowed move between two iterations (in # * STEP)
LAMBDA        = -10.0   # Penalty term for the volume
VTARG         = 0.6     # The target volume (more like a mean to keep the volume away from 0)
INISTEP       = 1e-4    # The initial step of the gradient descent
P             = 5       # The exponent in the regularization of the minimum
K             = 3       # The eigenvalue we optimize
NUMEV         = 5       # The number of eigenvalues to consider (the expected multiplicity)
TOL           = 1e-3    # The relative tolerance when increasing the objective

# Paths to folders
RES     = "./res/"       # Directory for results
TESTDIR = RES + "test/"  # Directory for test of libraries
SCRIPT  = "./sources/"   # Directory for sources

# Call for the executables of external codes
FREEFEM = "FreeFem++ -nw"

# Path to FreeFem scripts
FFTEST         = SCRIPT + "testFF.edp"
FFDESCENT      = SCRIPT + "descent.edp"
FFITERATE      = SCRIPT + "iterate.edp"
FFINIMSH       = SCRIPT + "inimsh.edp"
FFINILS        = SCRIPT + "inils.edp"
FFEIGENPROBLEM = SCRIPT + "eigenproblem.edp"
FFEIGENVALUE   = SCRIPT + "eigenvalue.edp"
FFGRADEV       = SCRIPT + "gradEv.edp"
FFVOL          = SCRIPT + "volume.edp"
FFGRADV        = SCRIPT + "gradV.edp"
FFOBJECTIVE    = SCRIPT + "objective.edp"
FFSIZEMAP      = SCRIPT + "sizemap.edp"
FFINTERPOLATE  = SCRIPT + "interpolate.edp"

# Names of output and exchange files
EXCHFILE = RES + "exch.data"
DEFMMG2D = "DEFAULT.mmg2d"
LOGFILE  = RES + "log.data"
HISTO    = RES + "histo.data"
STEP     = RES + "step"
TMPSOL   = "./res/temp.sol"
TESTMESH = TESTDIR + "test.mesh"
TESTPHI  = TESTDIR + "test.phi.sol"
TESTSOL  = TESTDIR + "test.grad.sol"

# Shortcut for various file types
def step(n,typ) :
  return STEP + "." + str(n) + "." + typ

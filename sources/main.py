#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import os
import sys
import numpy as np
import subprocess
import path
import inout
import mshtools
import lstools
import inigeom
import mechtools

###############################################################
##################      START PROGRAM    ######################
###############################################################

print("*************************************************")
print("****** Neumann eigenvalue optimization **********")
print("*************************************************")

# Initialize folders and exchange files
inout.iniWF()

# Test the links with external C libraries
inout.testLib()

# Creation of the initial mesh an initial density
inigeom.iniGeom(path.step(0,"mesh"), path.step(0,"sol"))

# Resolution of the eigenvalue problem
u = [path.step(0,f"u_{i+path.K}.sol") for i in range(path.NUMEV)]   # The eigenfunctions files
mechtools.eigenproblem(path.step(0,"mesh"), path.step(0,"sol"), u)

# Calculation of the eigenvalue and the volume of the density
newEv  = mechtools.eigenvalues()
newvol = mechtools.volume(path.step(0,"mesh"),path.step(0,"sol"))
newObj = mechtools.objective(newEv, newvol)

print(f"*** Initialization: Eigenvalue {newEv} ; volume {newvol}")

# Coefficient for time step ( descent direction is scaled with respect to mesh size)
coef = 1.0

# Main loop
# At the beginning of each iteration, are available:
#    - the mesh $\¢alT^n$ of $D$ associated to the current shape $\Omega^n$;
#    - the solution to the linear elasticity equation on $\Omega^n$ (at the nodes of $D$).
#    - The compliance and volume of the shape

for n in range(0,path.MAXIT) :
    # The names of the files containing...
    curmesh     = path.step(n,"mesh")            # The mesh
    newmesh     = path.step(n+1,"mesh")
    curRho      = path.step(n,"sol")           # The density
    newRho      = path.step(n+1,"sol")
    curVgrad    = path.step(n,"V.grad.sol")     # the gradient of the volume
    curgrad     = path.step(n,"grad.sol")        # the gradient of the objective
    curEvgrad   = [path.step(n,f"Ev_{i+path.K}.grad.sol") for i in range(path.NUMEV)]     # the gradient of the eigenvalue
    curu        = [path.step(n,f"u_{i+path.K}.sol") for i in range(path.NUMEV)]          # The eigenfunctions
    newu        = [path.step(n+1,f"u_{i+path.K}.sol") for i in range(path.NUMEV)]          # The new eigenfunctions

    curEv   = newEv
    curvol  = newvol
    curObj  = newObj

    print(f"Iteration {n}:")
    print(f"    Eigenvalues {curEv}")
    print(f"    Volume {curvol}")
    print(f"    Objective {curObj}")
    print(f"    Coef {coef}")

    # Print values in the path.HISTO file
    inout.printHisto(n,curObj,curvol)

    # Calculation of the gradients of compliance and volume
    mechtools.gradEv(curmesh,curRho,curEv,curu,curEvgrad)
    mechtools.gradV(curmesh,curVgrad)

    # Calculation of a descent direction
    mechtools.descent(curmesh,curEvgrad,curVgrad,curgrad)

    for k in range(path.MAXITLS):
        print(f"    Line search k = {k}")

        # Perfoms an iteration
        mechtools.iterate(curmesh, curRho, curgrad, newmesh, newRho, coef*path.INISTEP)

        # Adapt mesh after enough iterations
        if (n+1)%path.ITREMESH == 0:
            mshtools.adapt(newmesh, newRho, newmesh, newRho)

            


        # Solves the eigen problem and compute the new eigenvalues and volume
        mechtools.eigenproblem(newmesh, newRho, newu)
        newEv  = mechtools.eigenvalues()
        newvol = mechtools.volume(newmesh, newRho)

        # Compute the new volume and eigenvalue
        newObj = mechtools.objective(newEv, newvol)

        # Update the coef : increase if the objective was better
        if newObj > curObj - path.TOL*abs(curObj) or coef < path.MINCOEF or k == path.MAXITLS -1:
            coef = min(path.MAXCOEF, 1.1*coef)
            print(f"    Iteration {n} - subiteration {k} accepted\n")
            break
        else :
            print(f"    Iteration {n} - subiteration {k} rejected")
            proc = subprocess.Popen([f"rm {newmesh}"],shell=True)
            proc.wait()
            coef = max(path.MINCOEF, 0.6*coef)


###############################################################
####################       END PROGRAM      ###################
###############################################################
print("*************************************************")
print("****************** End **************************")
print("*************************************************")

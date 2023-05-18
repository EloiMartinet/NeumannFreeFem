#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import path
import subprocess
import os
import inout
import sys
import numpy as np

##############################################################################################################
######   Call to mmg2d                                                                                  ######
######   Inputs:   mesh (string) name of the mesh                                                       ######
######             ls   (int)  0 for standard remeshing mode, 1 for L.S. discretization mode            ######
######             phi  (string) name of the L.S. function                                              ######
######             hmin (real) minimum desired size of an element in the mesh                           ######
######             hmax (real) maximum desired size of an element in the mesh                           ######
######             hausd (real) geometric approximation parameter                                       ######
######             hgrad (real) mesh gradation parameter                                                ######
######             nr (int) 0 if identification of sharp angles, 1 if no identification                 ######
######   Output:   out (string) name of the output mesh                                                 ######
######   Return: 1 if remeshing successful, 0 otherwise
##############################################################################################################

def mmg2d(mesh,ls,phi,hmin,hmax,hausd,hgrad,nr,out) :

  log = open(path.LOGFILE,'a')

  if  ls :
    if nr :
      proc = subprocess.Popen(["{mmg} {mesh} -ls -sol {sol} -hmin {hmin} -hmax {hmax} -hausd {hausd} -hgrad {hgrad} -nr {res} -rmc".format(mmg=path.MMG2D,mesh=mesh,sol=phi,hmin=hmin,hmax=hmax,hausd=hausd,hgrad=hgrad,res=out)],shell=True,stdout=log)
      proc.wait()
    else :
      proc = subprocess.Popen(["{mmg} {mesh} -ls -sol {sol} -hmin {hmin} -hmax {hmax} -hausd {hausd} -hgrad {hgrad} {res} -rmc".format(mmg=path.MMG2D,mesh=mesh,sol=phi,hmin=hmin,hmax=hmax,hausd=hausd,hgrad=hgrad,res=out)],shell=True,stdout=log)
      proc.wait()
  else :
    if nr :
      proc = subprocess.Popen(["{mmg} {mesh} -hmin {hmin} -hmax {hmax} -hausd {hausd} -hgrad {hgrad} -nr {res} -rmc".format(mmg=path.MMG2D,mesh=mesh,sol=phi,hmin=hmin,hmax=hmax,hausd=hausd,hgrad=hgrad,res=out)],shell=True,stdout=log)
      proc.wait()
    else :
      proc = subprocess.Popen(["{mmg} {mesh} -hmin {hmin} -hmax {hmax} -hausd {hausd} -hgrad {hgrad} {res} -rmc".format(mmg=path.MMG2D,mesh=mesh,sol=phi,hmin=hmin,hmax=hmax,hausd=hausd,hgrad=hgrad,res=out)],shell=True,stdout=log)
      proc.wait()

  log.close()
  if ( proc.returncode != 0 ) :
    return 0
  else :
    return 1

##############################################################################################################
##############################################################################################################


def adapt(mesh, sol, newMesh, newSol, ls=0.5):
    #
    # Adapt the mesh and solution provided as arguments and save them
    # The mesh is thinner where the gradient of sol is greater
    #

    sizemap = path.RES + "sizemap.sol"  # The size map for the remeshing
    tmpMesh = path.RES + "tmp.mesh"     # In the case where mesh = newMesh, this will be necessary

    # Set information in exchange file
    inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
    inout.setAtt(file=path.EXCHFILE,attname="NewMeshName",attval=tmpMesh)
    inout.setAtt(file=path.EXCHFILE,attname="SolName",attval=sol)
    inout.setAtt(file=path.EXCHFILE,attname="NewSolName",attval=newSol)
    inout.setAtt(file=path.EXCHFILE,attname="SizeMap",attval=sizemap)

    # Computation of the size map
    proc = subprocess.Popen([f"{path.FREEFEM} {path.FFSIZEMAP} > /dev/null 2>&1"],shell=True)
    proc.wait()

    if ( proc.returncode != 0 ) :
        proc = subprocess.Popen([f"{path.FREEFEM} {path.FFSIZEMAP}"],shell=True)
        proc.wait()
        print(f"Error in {path.FFSIZEMAP}; abort.")
        exit()

    # Remesh according to the sizemap
    proc = subprocess.Popen([f"{path.MMG2D} {mesh} -sol {sizemap} {tmpMesh} -rmc > /dev/null 2>&1"],shell=True)
    proc.wait()

    if ( proc.returncode != 0 ) :
        print("coucou")

    # Interpolate the solution on the new mesh
    proc = subprocess.Popen([f"{path.FREEFEM} {path.FFINTERPOLATE} > /dev/null 2>&1"],shell=True)
    proc.wait()

    if ( proc.returncode != 0 ) :
        proc = subprocess.Popen([f"{path.FREEFEM} {path.FFINTERPOLATE}"],shell=True)
        proc.wait()
        print(f"Error in {path.FFINTERPOLATE}; abort.")
        exit()

    # Rename the temporary mesh as newMesh
    proc = subprocess.Popen([f"mv {tmpMesh} {newMesh}"],shell=True)
    proc.wait()

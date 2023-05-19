#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import path
import subprocess
import os
import inout
import sys

###########################################################################
#######           Create initial mesh and density                   #######
#######             Input: - mesh (string) path to mesh             #######
#######                    - sol (string) path to rho               #######
###########################################################################
def iniGeom(mesh, rho) :

  # Fill in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="RhoName",attval=rho)

  # Call to FreeFem for creating the background mesh
  log = open(path.LOGFILE,'a')
  proc = subprocess.Popen([f"{path.FREEFEM} {path.FFINIMSH} > /dev/null 2>&1"],shell=True,stdout=log)
  proc.wait()
  log.close()

  if ( proc.returncode != 0 ) :
    print("Error in creation of initial mesh; abort.")
    exit()

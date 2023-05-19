#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import subprocess
import inout
import os
import path
import sys
import numpy as np

#####################################################################################
#######   Numerical solver for eigenvalue problem                             #######
#######       inputs: mesh (string): mesh of the shape                        #######
#######               rho (string): input density                             #######
#######               list_u (string): list of output eigenfunctions               #######
#####################################################################################

def eigenproblem(mesh, rho, list_u) :

    # Set information in exchange file
    inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
    inout.setAtt(file=path.EXCHFILE,attname="RhoName",attval=rho)

    for i in range(path.NUMEV):
        inout.setAtt(file=path.EXCHFILE,attname=f"UName{i+path.K}",attval=list_u[i])

    # Call to FreeFem
    proc = subprocess.Popen([f"{path.FREEFEM} {path.FFEIGENPROBLEM} > /dev/null 2>&1"],shell=True)
    proc.wait()

    if ( proc.returncode != 0 ) :
      subprocess.Popen([f"{path.FREEFEM} {path.FFEIGENPROBLEM}"],shell=True)
      proc.wait()
      print(f"Error in {path.FFEIGENPROBLEM}; abort.")
      exit()

#####################################################################################
#####################################################################################

#####################################################################################
#######   Compute eigenvalue, being given the eigenfunction                   #######
#######       inputs: mesh (string): mesh of the shape                        #######
#######               rho (string): input density                             #######
#######               u (string): output eigenfunction                        #######
#####################################################################################

def eigenvalues() :
    #
    # This function supposes that the function eigenproblem have been called
    #
    eigenvalues = np.zeros(path.NUMEV)

    for i in range(path.NUMEV):
        [eigenvalues[i]] = inout.getrAtt(file=path.EXCHFILE,attname=f"Ev{path.K+i}")

    return eigenvalues

#####################################################################################
#####################################################################################

#####################################################################################
#######   Calculate volume                                                    #######
#######       input: mesh (string): mesh of the shape                         #######
#####################################################################################

def volume(mesh, rho) :

  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="RhoName",attval=rho)

  # Call to FreeFem
  proc = subprocess.Popen([f"{path.FREEFEM} {path.FFVOL} > /dev/null 2>&1"],shell=True)
  proc.wait()

  if ( proc.returncode != 0 ) :
    print(f"Error in {path.FFVOL}; abort.")
    exit()

  [vol] = inout.getrAtt(file=path.EXCHFILE,attname="Volume")

  return vol

def objective(eigenvalues, vol):
    #
    # Compute the objective function
    #
    obj = vol*np.power(np.sum(np.power(eigenvalues, -path.P)), -1./path.P)
    obj += path.LAMBDA*(vol - path.VTARG)**2

    return obj

#####################################################################################
#####################################################################################

#####################################################################################
#######   Calculate gradient of the compliance functional                     #######
#######       input:  mesh (string): mesh of the shape                        #######
#######               disp (string): solution of the elasticity system        #######
#######       output: grad (string): shape gradient of compliance             #######
#####################################################################################

def gradEv(mesh,rho,ev,list_u,list_gradEv) :

    # Set information in exchange file
    inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
    inout.setAtt(file=path.EXCHFILE,attname="RhoName",attval=rho)
    inout.setAtt(file=path.EXCHFILE,attname="Eigenvalue",attval=ev)

    for i in range(path.NUMEV):
        inout.setAtt(file=path.EXCHFILE,attname=f"UName{i+path.K}",attval=list_u[i])
        inout.setAtt(file=path.EXCHFILE,attname=f"GradEvName{i+path.K}",attval=list_gradEv[i])


    # Call to FreeFem
    proc = subprocess.Popen([f"{path.FREEFEM} {path.FFGRADEV} > /dev/null 2>&1"],shell=True)
    proc.wait()

    if ( proc.returncode != 0 ) :
        proc = subprocess.Popen([f"{path.FREEFEM} {path.FFGRADEV}"],shell=True)
        proc.wait()
        print(f"Error in {path.FFGRADEV}; abort.")
        exit()

#####################################################################################
#####################################################################################

#####################################################################################
#######   Calculate gradient of the volume function                           #######
#######       input:  mesh (string): mesh of the shape                        #######
#######       output: grad (string): shape gradient of volume                 #######
#####################################################################################

def gradV(mesh,grad) :

  # Set information in exchange file
  inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
  inout.setAtt(file=path.EXCHFILE,attname="GradName",attval=grad)

  # Call to FreeFem
  proc = subprocess.Popen([f"{path.FREEFEM} {path.FFGRADV} > /dev/null 2>&1"],shell=True)
  proc.wait()

  if ( proc.returncode != 0 ) :
    print("Error in calculation of gradient of volume; abort.")
    exit()

#####################################################################################
#####################################################################################

#######################################################################################
#####             Calculation of the (normalized) descent direction               #####
#####      inputs :   mesh: (string for) mesh ;                                   #####
#####                 phi: (string for) ls function                               #####
#####                 gCp: (string for) gradient of Compliance                    #####
#####                 Cp: (real) value of Compliance                              #####
#####                 gV: (string for) gradient of Volume                         #####
#####                 vol: (real) value of volume                                 #####
#####      Output:    g: (string for) total gradient                              #####
#######################################################################################

def descent(mesh,list_gEv,gV,grad) :
    #
    # This function supposes that the funciton eigenproblem has been called before
    #
    inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
    inout.setAtt(file=path.EXCHFILE,attname="GradVolName",attval=gV)
    inout.setAtt(file=path.EXCHFILE,attname="GradName",attval=grad)

    for i in range(path.NUMEV):
        inout.setAtt(file=path.EXCHFILE,attname=f"GradEvName{path.K+i}",attval=list_gEv[i])

    # Velocity extension - regularization via FreeFem
    proc = subprocess.Popen([f"{path.FREEFEM} {path.FFDESCENT} > /dev/null 2>&1"],shell=True)
    proc.wait()

    if ( proc.returncode != 0 ) :
        proc = subprocess.Popen([f"{path.FREEFEM} {path.FFDESCENT}"],shell=True)
        proc.wait()
        print(f"Error in {path.FFDESCENT}; abort.")
        exit()



# Perfoms one step of projected gradient
def iterate(mesh,rho,grad,newmesh, newRho, step) :

    # Set information in exchange file
    inout.setAtt(file=path.EXCHFILE,attname="MeshName",attval=mesh)
    inout.setAtt(file=path.EXCHFILE,attname="NewMeshName",attval=newmesh)
    inout.setAtt(file=path.EXCHFILE,attname="RhoName",attval=rho)
    inout.setAtt(file=path.EXCHFILE,attname="NewRhoName",attval=newRho)
    inout.setAtt(file=path.EXCHFILE,attname="GradName",attval=grad)
    inout.setAtt(file=path.EXCHFILE,attname="Step",attval=step)

    # Velocity extension - regularization via FreeFem
    proc = subprocess.Popen([f"{path.FREEFEM} {path.FFITERATE} > /dev/null 2>&1"],shell=True)
    proc.wait()

    if ( proc.returncode != 0 ) :
        proc = subprocess.Popen([f"{path.FREEFEM} {path.FFITERATE}"],shell=True)
        proc.wait()
        print(f"Error in {path.FFITERATE}; abort.")
        exit()

#######################################################################################
#######################################################################################

#!/usr/bin/pythonw
# -*-coding:Utf-8 -*

import path
import subprocess
import os
import sys
import numpy

##############################################################
######          Set the field attname in file          #######
##############################################################

def setAtt(file="none",attname="none",attval="none"):
  """ Set the value attval in the field attname of file """

  # Open file
  ff = open(file,"r")
  content = ff.read()
  contentl = content.lower()
  lst = content.split()
  lstl = contentl.split()
  ff.close()

  isfnd = 0
  # Travel file
  for i,elt in enumerate(lstl) :
    if elt == attname.lower() :
      isfnd = 1
      ind = i+1
      lst[ind] = str(attval)
      break

  # If attname has been found, rewrite file out of the updated list
  if isfnd :
    with open(file,"w") as ff :
      for i,elt in enumerate(lst) :
        ff.write(elt+"\n")
        if ( i % 2 == 1 ) :
            ff.write("\n")

  # If attname has not been found, append at the end of the file
  else :
    with open(file,"a") as ff :
      ff.write(attname+"\n"+str(attval)+"\n\n")

##############################################################
##############################################################

##############################################################
###########    Get real value associated to kwd    ###########
#####      npar = number of real parameters to obtain     ####
##############################################################

def getrAtt(file="none",attname="none",npar=1) :
  """ Get real value associated to keyword kwd in file """

  # Open file
  ff = open(file,"r")
  content = ff.read()
  content = content.lower()
  lst = content.split()
  ff.close()

  # Travel file
  rval = []
  for i,elt in enumerate(lst) :
    if elt == attname.lower() :
      for j in range(1,npar+1) :
        rval.append(float(lst[i+j]))

  return ( rval )

##############################################################
##############################################################

#######################################################################
######           Initialize folders and exchange files           ######
#######################################################################

def iniWF():

  # Create and clear ./res folder for results depending on the situation
  proc = subprocess.Popen(["mkdir -p {folder}".format(folder=path.RES)],shell=True)
  proc.wait()
  proc = subprocess.Popen(["rm -rf {folder}*".format(folder=path.RES)],shell=True)
  proc.wait()

  # Create and clear ./testdir folder for results depending on the situation
  proc = subprocess.Popen(["mkdir -p {folder}".format(folder=path.TESTDIR)],shell=True)
  proc.wait()
  proc = subprocess.Popen(["rm -rf {folder}*".format(folder=path.TESTDIR)],shell=True)
  proc.wait()

  # Create exchange file
  ff = open(path.EXCHFILE,'w')
  ff.close()

  # Create log file
  ff = open(path.LOGFILE,'w')
  ff.close()

  # Create histo file
  ff = open(path.HISTO,'w')
  ff.close()

  # Add global information (e.g. about Dirichlet and Neumann boundaries)
  setAtt(file=path.EXCHFILE,attname="HMesh",attval=path.HMESH)
  setAtt(file=path.EXCHFILE,attname="Regularization",attval=path.ALPHA)
  setAtt(file=path.EXCHFILE,attname="Eps",attval=path.EPS)
  setAtt(file=path.EXCHFILE,attname="P",attval=path.P)
  setAtt(file=path.EXCHFILE,attname="K",attval=path.K)
  setAtt(file=path.EXCHFILE,attname="NumEv",attval=path.NUMEV)
  setAtt(file=path.EXCHFILE,attname="Lambda",attval=path.LAMBDA)
  setAtt(file=path.EXCHFILE,attname="VTarg",attval=path.VTARG)

##############################################################
##############################################################

##############################################################################
######        Test calls to external C libraries and softwares          ######
##############################################################################

def testLib():

  log = open(path.LOGFILE,'a')

  # Test call to FreeFem
  setAtt(file=path.EXCHFILE,attname="MeshName",attval=path.TESTMESH)
  setAtt(file=path.EXCHFILE,attname="PhiName",attval=path.TESTPHI)
  setAtt(file=path.EXCHFILE,attname="SolName",attval=path.TESTSOL)

  proc = subprocess.Popen(["{FreeFem} {test} > /dev/null 2>&1".format(FreeFem=path.FREEFEM,test=path.FFTEST)],shell=True)
  proc.wait()

  if ( proc.returncode == 0 ) :
    print("FreeFem installation working.")
  else :
    print("Problem with FreeFem installation.")
    exit()


##############################################################################
##############################################################################

#################################################################################
######        Fill history file with compliance and volume values          ######
######            Inputs: it (int) number of the iteration                 ######
######                    Cp (real) value of compliance                    ######
######                    vol (real) value of volume                       ######
#################################################################################

def printHisto(it,Cp,vol):

  histo = open(path.HISTO,'a')
  print("{} {} {}".format(it,Cp,vol),file=histo)
  histo.close()

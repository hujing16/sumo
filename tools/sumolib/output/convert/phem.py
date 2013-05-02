"""
@file    phem.py
@author  Daniel Krajzewicz
@date    2013-01-15
@version $Id$

This module includes functions for converting SUMO's fcd-output into
data files read by PHEM.

SUMO, Simulation of Urban MObility; see http://sumo.sourceforge.net/
Copyright (C) 2013 DLR (http://www.dlr.de/) and contributors
All rights reserved
"""
import sumolib
import math








def _convType(tID):
  if tID.lower().startswith("passenger") or tID.lower().startswith("PKW"):
    return "PKW"
  if tID.lower().startswith("bus"):
    return "BUS"
  if tID.lower().startswith("heavy") or tID.lower().startswith("LKW"):
    return "LKW"
  print "Could not convert the vehicle type properly"
  return "unknown"

        
def fcd2dri(inpFCD, outSTRM, ignored):
  """
  Reformats the contents of the given fcd-output file into a .dri file, readable
  by PHEM. The fcd-output "fcd" must be a valid file name of an fcd-output.

  The following may be a matter of changes:
  - the engine torque is not given 
  """
  #print >> outSTRM, "v1\n<t>,<v>,<grad>,<n>\n[s],[km/h],[%],[1/min]\n"
  print >> outSTRM, "v1\n<t>,<v>,<grad>\n[s],[km/h],[%]"
  for q in inpFCD:
    if q.vehicle:
      for v in q.vehicle:
        percSlope = math.sin(float(v.slope))*100.
        print >> outSTRM, "%s,%s,%s" % (sumolib._intTime(q.time), float(v.speed)*3.6, percSlope)



def net2str(net, outSTRM):
  """
  Writes the network object given as "inpNET" as a .str file readable by PHEM.
  Returns a map from the SUMO-road id to the generated numerical id used by PHEM.

  The following may be a matter of changes:
  - currently, only the positions of the start and the end nodes are written, 
    the geometry of the edge as defined in the SUMO-network is not exported.
    A map between the edge id and a segment to a numerical id would be necessary 
  """
  if outSTRM!=None:
    print >> outSTRM, "Str-Id,Sp,SegAnX,SegEnX,SegAnY,SegEnY"
  sIDm = sumolib._Running()
  for e in net._edges:
    eid = sIDm.g(e._id)
    if outSTRM!=None:
      c1 = e._from._coord
      c2 = e._to._coord
      print >> outSTRM, "%s,%s,%s,%s,%s,%s" % (eid, len(e._lanes), c1[0], c2[0], c1[1], c2[1])
  return sIDm 



def fcd2fzp(inpFCD, outSTRM, further):
  """
  Reformats the contents of the given fcd-output file into a .fzp file, readable
  by PHEM. The fcd-output "fcd" must be a valid file name of an fcd-output.
  
  The "sIDm" parameter must be a map from SUMO-edge ids to their numerical 
  representation as generated by toSTR(inpNET, outSTRM).
  Returns two maps, the first from vehicle ids to a numerical representation,
  the second from vehicle type ids to a numerical representation.
  """
  sIDm = further["phemStreetMap"]
  if outSTRM!=None:
    print >> outSTRM, "t,WeltX,WeltY,Veh. No,v,Gradient,veh.Typ-Id,Str-Id"
  vIDm = sumolib._Running()
  vtIDm = sumolib._Running()
  vtIDm.g("PKW")
  vtIDm.g("LKW")
  vtIDm.g("BUS")
  for q in inpFCD:
    if q.vehicle:
      for v in q.vehicle:
        vid = vIDm.g(v.id)
        aType = _convType(v.type)
        vtid = vtIDm.g(aType)
        sid = sIDm.g(sumolib._laneID2edgeID(v.lane))
        percSlope = math.sin(float(v.slope))*100.
        if outSTRM!=None:  
          print >> outSTRM, "%s,%s,%s,%s,%s,%s,%s,%s" % (
                  sumolib._intTime(q.time), float(v.x), float(v.y), 
                  vid, float(v.speed)*3.6, percSlope, vtid, sid)
  return vIDm, vtIDm
  
  
  
def vehicleTypes2flt(outSTRM, vtIDm):
  """
  Currently, rather a stub than an implementation. Writes the vehicle ids stored
  in the given "vtIDm" map formatted as a .flt file readable by PHEM.

  The following may be a matter of changes:               
  - A default map is assigned to all vehicle types with the same probability 
  """
  for q in vtIDm._m:
    print >> outSTRM, "%s,%s,%s" % (vtIDm.g(q), "<VEHDIR>\PC\PC_%s.GEN" % q, 1.)


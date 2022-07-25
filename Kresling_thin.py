
#Kristen L. Dorsey
#K.Dorsey@northeastern.edu

import adsk.core, adsk.fusion, adsk.cam
import math

#Kresling dimensions
R = 1 #Radius of Kresling "polygon" in cm
t = 0.1 #Thickness of the Kresling face in cm 
N = 6 #Number of Kresling polygon faces
alpha = 12 #angle in degrees
L1 = 2.5 #Uncompressed length/height
makeBase = 0 #Make the base of the Kresling? (Boolean)

#Hinge and wall thicknesses
hingeT = t
wallT = 3*t

def PolygonPoints(N,offsetAngle,xAxis):
    #Generate the polygon points for a Kresling polygon. By convention, bottom face should be alpha = 0. 
    # Offset is +/- phi for the orthogonal points
    #Create N points in X or Y
    #subtracting pi/2 (xAxis val) translates from cos to sin to get Y axis value

    pgonPts = [math.cos((2*k*math.pi/N)-offsetAngle-xAxis) for k in range(N)]
    return pgonPts 

def genSketch(pX,pY,pZ):
    #Generalized sketch from point list in X, Y, Z
    newSketch = sketchObjs.add(rootComp.xYConstructionPlane)

    numLines = len(pX)
	
    #define a shape two points at a time
    KresLines = newSketch.sketchCurves.sketchLines
    for k in range(numLines):
        #Wrap around to 0th point again to enclose the polygon
        dP0 = adsk.core.Point3D.create(pX[k], pY[k], pZ[k])
        dP1 = adsk.core.Point3D.create(pX[((k+1)%numLines)], pY[((k+1)%numLines)], pZ[((k+1)%numLines)])
    
        #draw the shape by adding the line
        KresSketch = KresLines.addByTwoPoints(dP0,dP1)
    
    profile = newSketch.profiles.item(0)

    return profile     

def AddLoftFeature(loftFeatures,profileObjArray):
    loftInput = loftFeatures.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    loft0 = loftInput.loftSections
    for x in profileObjArray:
        loft0.add(x)
    loftInput.isSolid = True #True for solid, False for hollow shape
    loftOutput = loftFeatures.add(loftInput)
    return loftOutput

def makeBasePgon(pLEX,pLEY,t,lofts,bodyList):
    N = len(pLEX)
    #Take bottom exterior points and create two drawings at spacing t from each other
    KLidL = genSketch(pLEX,pLEY,[-t for k in range(N)])
    KLidU = genSketch(pLEX,pLEY,[0 for k in range(N)])
    loftLid = AddLoftFeature(lofts,[KLidL,KLidU])
    
    bodyKLid = loftLid.bodies.item(0)
    bodyList.append(bodyKLid) 
    return bodyList

def paramKresling(R,pX,pY,pZ):
    #Multiply all points by radius
    pXP = [i*R for i in pX]
    pYP = [i*R for i in pY]

    #Make the Kresling triangle drawing
    KreslingProfileP = genSketch(pXP,pYP,pZ)
    return KreslingProfileP

def makeKreslingBody(cPlanes,lofts,R0,R1,R2,N,L1,alpha,makeBase):
    #Create each Kresling triangle according to specified dimensions

    bodyList = [] #Make an empty body list to append new bodies to
    phi = math.pi/N

    #Create point lists for Kresling triangle points
    #nomenclature: point Lower/Upper External/Internal X/Y
    pLX = PolygonPoints(N,0,0)
    pUX = PolygonPoints(N,alpha,0)
    pLY = PolygonPoints(N,0,math.pi/2)
    pUY = PolygonPoints(N,alpha,math.pi/2)

    #Create point lists for orthogonal Kresling points to make thinner angles
    psXP = PolygonPoints(N,-phi,0) #Shift by phi instead of alpha
    psXN = PolygonPoints(N,phi,0)
    psYP = PolygonPoints(N,-phi,math.pi/2)
    psYN = PolygonPoints(N,phi,math.pi/2)
   
    #Interleave two lists of points
    pXOrtho = [val for pair in zip(psXN, psXP) for val in pair]
    pYOrtho = [val for pair in zip(psYN, psYP) for val in pair]

    #Multiply all points in list by tcos(phi)
    pXOrtho = [i*((R1-R2)*math.cos(phi)) for i in pXOrtho]
    pYOrtho = [i*((R1-R2)*math.cos(phi)) for i in pYOrtho]

        #Create point lists for orthogonal Kresling points to make thinner angles
    psXPA = PolygonPoints(N,-phi+alpha,0) #Shift by phi instead of alpha
    psXNA = PolygonPoints(N,phi+alpha,0)
    psYPA = PolygonPoints(N,-phi+alpha,math.pi/2)
    psYNA = PolygonPoints(N,phi+alpha,math.pi/2)
   
    #Interleave two lists of points
    pXOrthoA = [val for pair in zip(psXNA, psXPA) for val in pair]
    pYOrthoA = [val for pair in zip(psYNA, psYPA) for val in pair]

    #Multiply all points in list by tcos(phi)
    pXOrthoA = [i*((R1-R2)*math.cos(phi)) for i in pXOrthoA]
    pYOrthoA = [i*((R1-R2)*math.cos(phi)) for i in pYOrthoA]

    #Draw upper and lower Kresling triangles from point lists
    for m in range(2):    
        for k in range(N):
            if m == 0: #make upper or lower triangle, m == 0 is lower
                #Make innermost Kresling triangle points
                pX = [pLX[k],pUX[k],pLX[(k+1)%N]]
                pY = [pLY[k],pUY[k],pLY[(k+1)%N]]
                pZ = [0,L1,0]

                offsetX = [pXOrtho[(2*k+1)%(2*N)],0,pXOrtho[(2*k+2)%(2*N)]]
                offsetY = [pYOrtho[(2*k+1)%(2*N)],0,pYOrtho[(2*k+2)%(2*N)]]

            else:
                pX = [pUX[k],pLX[(k+1)%N],pUX[(k+1)%N]]
                pY = [pUY[k],pLY[(k+1)%N],pUY[(k+1)%N]]
                pZ = [L1,0,L1]

                offsetX = [pXOrthoA[(2*k+1)%(2*N)],0,pXOrthoA[(2*k+2)%(2*N)]]
                offsetY = [pYOrthoA[(2*k+1)%(2*N)],0,pYOrthoA[(2*k+2)%(2*N)]]

            #problem is that only one side matches. Maybe alpha? Maybe m index?            

            pXOrtho2Draw = [R2*pX[0]+offsetX[0],R1*pX[1]+offsetX[1],R2*pX[2]+offsetX[2]]
            pYOrtho2Draw = [R2*pY[0]+offsetY[0],R1*pY[1]+offsetY[1],R2*pY[2]+offsetY[2]]

            #Make the orthogonal Kresling triangle
            KreslingProfileO= paramKresling(1,pXOrtho2Draw,pYOrtho2Draw,pZ)

            #Make the exterior Kresling triangle
            KreslingProfileE= paramKresling(R0,pX,pY,pZ)

            #Make the central Kresling triangle
            KreslingProfileC= paramKresling(R1,pX,pY,pZ)

            #Make the interior Kresling triangle
            KreslingProfileI= paramKresling(R2,pX,pY,pZ)

            #Loft between interior and exterior Kresling faces
            loftKE = AddLoftFeature(lofts,[KreslingProfileE,KreslingProfileC])
            loftKI = AddLoftFeature(lofts,[KreslingProfileO,KreslingProfileI])
        
            #Create bodies from loft features
            bodyKE = loftKE.bodies.item(0)
            bodyList.append(bodyKE)

            #Create bodies from loft features
            bodyKI = loftKI.bodies.item(0)
            bodyList.append(bodyKI)

             #Make Kresling base with thickness t
    if makeBase == 1:
        makeBasePgon([i*R0 for i in pLX],[i*R0 for i in pLY],(R0-R1),lofts,bodyList)

    return bodyList

##### Main code #####

# Create Fusion document 
app = adsk.core.Application.get()
ui = app.userInterface
doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
design = app.activeProduct

# Create sketch, construction plane, and loft objects
rootComp = design.rootComponent
sketchObjs = rootComp.sketches
cPlaneObjs = rootComp.constructionPlanes
loftFeats = rootComp.features.loftFeatures

#Define Kresling properties
alpha = (math.pi/180)*alpha

##Make Kresling structure
Kresling = makeKreslingBody(cPlaneObjs,loftFeats,R,R-hingeT,R-wallT,N,L1,alpha,makeBase)




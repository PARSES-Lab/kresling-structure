#Kristen L. Dorsey, Northeastern University

import adsk.core, adsk.fusion, adsk.cam
import math

#Kresling dimensions
R = 1.5 #Length of Kresling polygon face
t = 0.1 #Thickness of the Kresling in cm 
N = 6 #Number of Kresling polygon faces
alpha = math.pi*60/180
L1 = 3
makeBase = 0 #Make the base of the Kresling? (Boolean)

gamma = math.pi/N
P = R/math.sin(gamma) #Redefine R so that the dimensions are correct for center of Kresling polygon to one polygon angle

def PolygonPoints(P,N,alpha,X):
    #Generate the polygon points for top or bottom face. By convention, bottom face should be alpha = 0
    #Create N points in X or Y

    for k in range(N):
        if X==1:
            outerPts = [P*math.cos((2*k*math.pi/N)-alpha) for k in range(N)]
        else:
            outerPts = [P*math.sin((2*k*math.pi/N)-alpha) for k in range(N)]

    return outerPts

def CreateOffsetPlane(cPlanes,offsetWidth):
    offsetPlane = cPlanes.createInput()
    offset = adsk.core.ValueInput.createByString(str(offsetWidth)+'cm')
    offsetPlane.setByOffset(rootComp.xYConstructionPlane, offset)
    planeName = cPlanes.add(offsetPlane)
    return planeName

def CreateKTriangle(cPlanes,zOffS,p0,p1,p2):
    TriPlane = CreateOffsetPlane(cPlanes,zOffS)
    Triangle = sketchObjs.add(TriPlane)

    # #define the triangle points
    dP0 = adsk.core.Point3D.create(p0[0], p0[1], p0[2])
    dP1 = adsk.core.Point3D.create(p1[0], p1[1], p1[2])
    dP2 = adsk.core.Point3D.create(p2[0], p2[1], p2[2])
   
    #draw the triangle edges
    triLines = Triangle.sketchCurves.sketchLines
    lVLine = triLines.addByTwoPoints(dP0,dP1)
    lULine = triLines.addByTwoPoints(dP1,dP2)
    rULine = triLines.addByTwoPoints(dP2,dP0)
    
    profile = Triangle.profiles.item(0)

    return profile  

def KreslingPolygonSketch(cPlanes,pX,pY,pZ):
    TriPlane = CreateOffsetPlane(cPlanes,0)
    Triangle = sketchObjs.add(TriPlane)

    N = len(pX)

    #define the Kresling polygon
    KresLines = Triangle.sketchCurves.sketchLines
    for k in range(N):
        dP0 = adsk.core.Point3D.create(pX[k], pY[k], pZ)
        dP1 = adsk.core.Point3D.create(pX[((k+1)%N)], pY[((k+1)%N)], pZ)
    
        #draw the Kresling polygon by adding the line
        KresPLine = KresLines.addByTwoPoints(dP0,dP1)
    
    profile = Triangle.profiles.item(0)

    return profile     

def AddLoftFeature(loftFeatures,profileObjArray):
    loftInput = loftFeatures.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    loft0 = loftInput.loftSections
    for x in profileObjArray:
        loft0.add(x)
    loftInput.isSolid = True #True for solid, False for hollow shape
    loftOutput = loftFeatures.add(loftInput)
    return loftOutput

def makeKreslingBody(cPlanes,lofts,P,N,t,L1,alpha,makeBase):
    #Create each Kresling triangle according to specified dimensions

    bodyList = [] #Make an empty body list to append new bodies to

    #Lower and upper external Kresling triangle points
    pLEX = PolygonPoints(P,N,0,1)
    pUEX = PolygonPoints(P,N,alpha,1)
    pLEY = PolygonPoints(P,N,0,0)
    pUEY = PolygonPoints(P,N,alpha,0)

    #Lower and upper internal Kresling triangle points
    pLIX = PolygonPoints((P-t),N,0,1)
    pUIX = PolygonPoints((P-t),N,alpha,1)
    pLIY = PolygonPoints((P-t),N,0,0)
    pUIY = PolygonPoints((P-t),N,alpha,0)

    #Make upper and lower Kresling triangles
    for m in range(2):    
        for k in range(1):
            if m == 1: #determine upper or lower triangle
                pE0 = (pLEX[k],pLEY[k],0)
                pE1 = (pUEX[k],pUEY[k],L1)
                pE2 = (pLEX[(k+1)%N],pLEY[(k+1)%N],0)

                pI0 = (pLIX[k],pLIY[k],0) 
                pI1 = (pUIX[k],pUIY[k],L1)
                pI2 = (pLIX[(k+1)%N],pLIY[(k+1)%N],0)
            else:
                pE0 = (pUEX[k],pUEY[k],L1)
                pE1 = (pLEX[(k+1)%N],pLEY[(k+1)%N],0)
                pE2 = (pUEX[(k+1)%N],pUEY[(k+1)%N],L1)

                pI0 = (pUIX[k],pUIY[k],L1)
                pI1 = (pLIX[(k+1)%N],pLIY[(k+1)%N],0)
                pI2 = (pUIX[(k+1)%N],pUIY[(k+1)%N],L1)

            #Make the exterior Kresling triangle
            KreslingProfile0 = CreateKTriangle(cPlanes,0,pE0,pE1,pE2)
            
            #Make the interior Kresling triangle
            KreslingProfile1= CreateKTriangle(cPlanes,0,pI0,pI1,pI2)
            
            #Create lofts to form Kresling face with specified thickness
            loftK = AddLoftFeature(lofts,[KreslingProfile0,KreslingProfile1])
        
                    #Create bodies from loft features
            bodyK = loftK.bodies.item(0)
            bodyList.append(bodyK)

    #Make Kresling base
    if makeBase == 1:
        KLid0 = KreslingPolygonSketch(cPlanes,pLEX,pLEY,-t)
        KLid1 = KreslingPolygonSketch(cPlanes,pLEX,pLEY,0)
        loftLid = AddLoftFeature(lofts,[KLid0,KLid1])
    
        bodyKLid = loftLid.bodies.item(0)
        bodyList.append(bodyKLid)    

    return bodyList


##### Main code #####

# Create Fusion document 
app = adsk.core.Application.get()
ui = app.userInterface
doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
design = app.activeProduct

# Create sketch, construction plane, loft, and pattern objects
rootComp = design.rootComponent
sketchObjs = rootComp.sketches
cPlaneObjs = rootComp.constructionPlanes
loftFeats = rootComp.features.loftFeatures

##Make Kresling structure
Kresling = makeKreslingBody(cPlaneObjs,loftFeats,P,N,t,L1,alpha,makeBase)


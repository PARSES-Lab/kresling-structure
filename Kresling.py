'''
Kris Dorsey
K.Dorsey@Northeastern.edu
Kristen@Kristendorsey.com
This script is run from Autodesk Fusion 360 scripts and add ons interface
The sizing and equations come from Kaufman and Li 2021
'''

# adsk are libraries for Python Fusion API
import adsk.core, adsk.fusion, adsk.cam
import math

#Kresling dimensions

radius = 1
wall_thickness = 0.1 
height = 2.5
number_polygon_edges = 6 
top_rotation_angle = 12 

ratio_hinge_to_wall = 1
ratio_base_to_wall = 0
hinge_thickness = wall_thickness * ratio_hinge_to_wall
base_thickness = wall_thickness * ratio_base_to_wall

'''
Mapping from Kaufman to variables here
alpha -> top_rotation_angle
phi -> 
R -> radius
L1 -> height
N -> number_polygon_edges
'''

def generate_polygon_points(number_of_kresling_edges, offset_angle, sine_rotation):

    polygon_points = \
        [math.cos((2 * k * math.pi / number_of_kresling_edges) - offset_angle - sine_rotation) \
        for k in range(number_of_kresling_edges)]
	
    return polygon_points 

def gen_sketch(points_x, points_y, points_z):
    #Generalized sketch from point list in X, Y, Z
    newSketch = sketchObjs.add(rootComp.xYConstructionPlane)

    #define a shape two points at a time
    KresLines = newSketch.sketchCurves.sketchLines
    for k in range(len(points_x)):
        #Wrap around to 0th point again to enclose the polygon
        point0 = adsk.core.Point3D.create(points_x[k], points_y[k], points_z[k])
        point1 = adsk.core.Point3D.create(points_x[((k+1) % len(points_x))], points_y[((k+1) % len(points_x))], points_z[((k+1) % len(points_x))])
    
        #draw the shape by adding the line
        KresSketch = KresLines.addByTwoPoints(point0, point1)
    
    profile = newSketch.profiles.item(0)

    return profile     

def AddLoftFeature(loftFeatures,profileObjArray):
    #Lofts objects from sketch profiles
    loftInput = loftFeatures.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    loft0 = loftInput.loftSections
    for x in profileObjArray:
        loft0.add(x)
    loftInput.isSolid = True 
    loftOutput = loftFeatures.add(loftInput)
    return loftOutput

def makeBasePgon(lower_x_points, lower_y_points, thickness, lofts, bodyList):

    #Take bottom exterior points and create two drawings at spacing t from each other
    lid_lower_points = gen_sketch(lower_x_points, lower_y_points, [-thickness for k in range(len(lower_x_points))])
    lid_upper_points = gen_sketch(lower_x_points, lower_y_points, [0 for k in range(len(lower_x_points))])

    #Loft between lower Kresling polygon and upper Kresling polygon
    loftLid = AddLoftFeature(lofts,[lid_lower_points,lid_upper_points])
    
    bodyKLid = loftLid.bodies.item(0)
    bodyList.append(bodyKLid) 
    return bodyList

def paramKresling(radius, points_x, points_y, points_z):
    #Multiply all points by radius
    points_x_parameterized = [i * radius for i in points_x]
    points_y_parameterized = [i * radius for i in points_y]

    #Make the Kresling triangle drawing
    KreslingProfileP = gen_sketch(points_x_parameterized, points_y_parameterized, points_z)
    return KreslingProfileP

def makeKreslingBody(cPlanes,lofts, radius, wall_thickness, hinge_thickness, number_polygon_edges, height, top_rotation_angle, base_thickness):
    #Create each Kresling triangle according to specified dimensions

    bodyList = [] #Make an empty body list to append new bodies to
    phi = math.pi / number_polygon_edges

    #Create point lists for Kresling triangle points
    #nomenclature: point Lower/Upper External/Internal X/Y
    lower_x = generate_polygon_points(number_polygon_edges, 0, 0)
    upper_x = generate_polygon_points(number_polygon_edges, top_rotation_angle, 0)
    lower_y = generate_polygon_points(number_polygon_edges, 0, math.pi/2)
    upper_y = generate_polygon_points(number_polygon_edges, top_rotation_angle, math.pi/2)

    #Create point lists for orthogonal Kresling points to make thinner angles
    orthogonal_x_neg = generate_polygon_points(number_polygon_edges, -phi, 0) 
    orthogonal_x_pos = generate_polygon_points(number_polygon_edges, phi, 0)
    orthogonal_y_neg = generate_polygon_points(number_polygon_edges, -phi, math.pi/2)
    orthogonal_y_pos = generate_polygon_points(number_polygon_edges, phi, math.pi/2)
   
    #Interleave two lists of points
    orthogonal_x_lower = [val for pair in zip(orthogonal_x_neg, orthogonal_x_pos) for val in pair]
    orthogonal_y_lower = [val for pair in zip(orthogonal_y_neg, orthogonal_y_pos) for val in pair]

    orthogonal_x_lower = [i * ((wall_thickness - hinge_thickness) * math.cos(phi)) for i in orthogonal_x_lower]
    orthogonal_y_lower = [i * ((wall_thickness - hinge_thickness) * math.cos(phi)) for i in orthogonal_y_lower]

    #Create point lists for orthogonal Kresling points to make thinner angles
    #may have flipped the sign here
    orthogonal_x_neg = generate_polygon_points(number_polygon_edges, -phi + top_rotation_angle , 0) 
    orthogonal_x_pos = generate_polygon_points(number_polygon_edges, phi + top_rotation_angle , 0)
    orthogonal_y_neg = generate_polygon_points(number_polygon_edges, -phi + top_rotation_angle , math.pi/2)
    orthogonal_y_pos = generate_polygon_points(number_polygon_edges, phi + top_rotation_angle , math.pi/2)
   
    #Interleave two lists of points
    orthogonal_x_upper = [val for pair in zip(orthogonal_x_neg, orthogonal_x_pos) for val in pair]
    orthogonal_y_upper = [val for pair in zip(orthogonal_y_neg, orthogonal_y_pos) for val in pair]

    #Multiply all points in list by tcos(phi)
    orthogonal_x_upper = [i * ((wall_thickness - hinge_thickness) * math.cos(phi)) for i in orthogonal_x_upper]
    orthogonal_y_upper = [i * ((wall_thickness - hinge_thickness) * math.cos(phi)) for i in orthogonal_y_upper]

    #Draw upper and lower Kresling triangles from point lists
    for m in range(2):    
        for k in range(number_polygon_edges):
            if m == 0: #make upper or lower triangle, m == 0 is lower
                #Make innermost Kresling triangle points
                pointsX = [lower_x[k], upper_x[k], lower_x[(k+1) % number_polygon_edges]]
                pointsY = [lower_y[k], upper_y[k], lower_y[(k+1) % number_polygon_edges]]
                pointsZ = [0, height, 0]

                if hinge_thickness < wall_thickness:
                    offsetX = [orthogonal_x_lower[(2 * k + 1) % (2 * number_polygon_edges)], 0, orthogonal_x_lower[(2 * k + 2) % (2 * number_polygon_edges)]]
                    offsetY = [orthogonal_y_lower[(2 * k + 1) % (2 * number_polygon_edges)], 0, orthogonal_y_lower[(2 * k + 2) % (2 * number_polygon_edges)]]

            else:
                pointsX = [upper_x[k],lower_x[(k + 1) % number_polygon_edges], upper_x[(k+1) % number_polygon_edges]]
                pointsY = [upper_y[k],lower_y[(k + 1) % number_polygon_edges], upper_y[(k+1) % number_polygon_edges]]
                pointsZ = [height, 0, height]

                if hinge_thickness < wall_thickness:
                    offsetX = [orthogonal_x_upper[(2 * k + 1) % (2 * number_polygon_edges)], 0, orthogonal_x_upper[(2 * k + 2) % (2 * number_polygon_edges)]]
                    offsetY = [orthogonal_y_upper[(2 * k + 1) % (2 * number_polygon_edges)], 0, orthogonal_y_upper[(2 * k + 2) % (2 * number_polygon_edges)]]

            #Make the Kresling triangles
            outer_kresling= paramKresling(radius, pointsX, pointsY, pointsZ)
            center_kresling= paramKresling(radius - hinge_thickness, pointsX, pointsY, pointsZ)
            
            #Loft between interior and exterior Kresling faces
            outer_loft = AddLoftFeature(lofts,[outer_kresling,center_kresling]) 

            #Create bodies from loft features
            outer_bodies = outer_loft.bodies.item(0)
            bodyList.append(outer_bodies)

            if hinge_thickness < wall_thickness:
                pXOrtho2Draw = [(radius-wall_thickness) * pointsX[0] + offsetX[0], (radius-hinge_thickness) * pointsX[1] + offsetX[1], (radius-wall_thickness) * pointsX[2] + offsetX[2]]
                pYOrtho2Draw = [(radius-wall_thickness) * pointsY[0] + offsetY[0], (radius-hinge_thickness) * pointsY[1] + offsetY[1], (radius-wall_thickness) * pointsY[2] + offsetY[2]]    

                inner_kresling= paramKresling(radius - wall_thickness, pointsX, pointsY, pointsZ)
                orthogonal_kresling= paramKresling(1, pXOrtho2Draw, pYOrtho2Draw, pointsZ)    
                inner_loft = AddLoftFeature(lofts,[orthogonal_kresling,inner_kresling])
        
                #Create bodies from loft features
                inner_bodies = inner_loft.bodies.item(0)
                bodyList.append(inner_bodies)

    if base_thickness > 0:
        makeBasePgon([i * radius for i in lower_x],[i * radius for i in lower_y], base_thickness, lofts, bodyList)

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

#Convert rotation angles to radians
top_rotation_angle = (math.pi/180)*top_rotation_angle

##Make Kresling structure
Kresling = makeKreslingBody(cPlaneObjs,loftFeats, radius , wall_thickness, hinge_thickness, number_polygon_edges, height , top_rotation_angle, base_thickness)




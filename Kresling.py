'''
Kris Dorsey, Sonia Roberts, and Ash Wu
K.Dorsey@Northeastern.edu
Kristen@Kristendorsey.com
This script is run from Autodesk Fusion 360 scripts and add ons interface
The sizing and equations come from Kaufman and Li 2021
Mapping from Kaufman to variables here
Assumes bottom rotation angle is 0
alpha -> top_rotation_angle
R -> radius
P -> edge_length
L1 -> height
N -> number_polygon_edges
phi -> half_inner_angle
'''

# adsk are libraries for Python Fusion API
import adsk.core, adsk.fusion, adsk.cam
import math

#Kresling dimensions 
# all in cm
edge_length = 3
height = 4.07
number_polygon_edges = 6 
top_rotation_angle = 30 # in degrees 
wall_thickness = 0.1
hinge_thickness = 0.1
chamber_length = 0

#Calculate hinge and base thicknesses from ratios (do not change these values)
#hinge_thickness = wall_thickness * ratio_hinge_to_wall
ratio_base_to_wall = 1
ratio_lip_to_wall = 1

base_thickness = (wall_thickness + hinge_thickness) * ratio_base_to_wall
lip_thickness = (wall_thickness + hinge_thickness) * ratio_lip_to_wall

radius = edge_length * (2 * math.sin( math.pi / number_polygon_edges ))

#general purpose methods to generate Kresling points, sketches, and lofts

def generate_polygon_points(number_of_kresling_edges, wall_fraction, offset_angle, sine_rotation):
    polygon_points = \
        [math.cos((2 * k * math.pi / number_of_kresling_edges) - offset_angle - sine_rotation) \
        for k in range(number_of_kresling_edges)]
    
    low_wall_points = \
        [wall_fraction * math.cos((2*(k - 1) * math.pi) / number_of_kresling_edges - offset_angle - sine_rotation) \
         for k in range(number_of_kresling_edges)]
    
    last_val = low_wall_points.pop(0)
    low_wall_points.append(last_val)

    high_wall_points = \
        [wall_fraction * math.cos((2*(k + 1) * math.pi) / number_of_kresling_edges - offset_angle - sine_rotation) \
         for k in range(number_of_kresling_edges)]
	
    return [polygon_points, high_wall_points, low_wall_points] 

def gen_sketch(points_x, points_y, points_z):
    #Generalized sketch from point list in X, Y, Z
    new_sketch = sketchObjs.add(rootComp.xYConstructionPlane)

    #define a shape two points at a time
    Kres_lines = new_sketch.sketchCurves.sketchLines
    for k in range(len(points_x)):
        #Wrap around to 0th point again to enclose the polygon
        point0 = adsk.core.Point3D.create(points_x[k], points_y[k], points_z[k])
        point1 = adsk.core.Point3D.create(points_x[((k+1) % len(points_x))], points_y[((k+1) % len(points_x))], points_z[((k+1) % len(points_x))])
    
        #draw the shape by adding the line
        Kres_sketch = Kres_lines.addByTwoPoints(point0, point1)
    
    profile = new_sketch.profiles.item(0)
    return profile     

def param_Kresling(radius, points_x, points_y, points_z):
    #Multiply all points by radius
    points_x_parameterized = [i * radius for i in points_x]
    points_y_parameterized = [i * radius for i in points_y]

    #Make the Kresling triangle drawing
    Kresling_profile = gen_sketch(points_x_parameterized, points_y_parameterized, points_z)
    return Kresling_profile

def add_loft(loft_features,profile_obj_array):
    #Lofts objects from sketch profiles
    loft_input = loft_features.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    loft0 = loft_input.loftSections
    for x in profile_obj_array:
        loft0.add(x)
    loft_input.isSolid = True 
    loft_output = loft_features.add(loft_input)
    return loft_output

#base generation

def make_base(upper_x_points, upper_y_points, radius, height, thickness, lofts, body_list):

    #Take exterior points and create two drawings at spacing t from each other
    lip_lower_points = gen_sketch([i * radius for i in upper_x_points], [i * radius for i in upper_y_points], [height for k in range(len(upper_x_points))])
    lip_upper_points = gen_sketch([i * radius for i in upper_x_points], [i * radius for i in upper_y_points], [height + thickness for k in range(len(upper_x_points))])

    #Loft between two drawings to make base
    loft_lip = add_loft(lofts,[lip_lower_points,lip_upper_points])
    
    body_K_lip = loft_lip.bodies.item(0)
    body_list.append(body_K_lip) 
    
    return body_list

def make_Kresling_body(lofts, radius, wall_thickness, hinge_thickness, number_polygon_edges, height, top_rotation_angle, base_thickness, lip_thickness):
    #Create each Kresling triangle according to specified dimensions

    body_list = [] #Make an empty body list to append new bodies to

    wall_fraction = wall_thickness / radius
    #Create point lists for Kresling triangle points
    lower_x = generate_polygon_points(number_polygon_edges, wall_fraction, 0, 0)
    upper_x = generate_polygon_points(number_polygon_edges, wall_fraction, top_rotation_angle, 0)
    lower_y = generate_polygon_points(number_polygon_edges, wall_fraction, 0, math.pi/2)
    upper_y = generate_polygon_points(number_polygon_edges, wall_fraction, top_rotation_angle, math.pi/2)
 
    #Draw upper and lower Kresling triangles from point lists
    for m in range(2):    
        for k in range(number_polygon_edges):

            if m == 0: #make upper or lower triangle, m == 0 is lower

                points_z = [0, height, 0]
                points_z_wall = [0.1, 3.97, 0.1]
                points_x = [lower_x[0][k], upper_x[0][k], lower_x[0][(k + 1) % number_polygon_edges]]
                points_y = [lower_y[0][k], upper_y[0][k], lower_y[0][(k + 1) % number_polygon_edges]]

                hinge_x = [lower_x[1][k] + lower_x[0][k], upper_x[0][k] * (1+ wall_fraction), lower_x[2][(k) % number_polygon_edges] + lower_x[0][(k + 1) % number_polygon_edges]]
                hinge_y = [lower_y[1][k] + lower_y[0][k], upper_y[0][k] * (1+ wall_fraction), lower_y[2][(k) % number_polygon_edges] + lower_y[0][(k + 1) % number_polygon_edges]]
        
            else:
                points_z = [height, 0, height]
                points_z_wall = [3.97, 0.1, 3.97]
                points_x = [upper_x[0][k],lower_x[0][(k + 1) % number_polygon_edges], upper_x[0][(k + 1) % number_polygon_edges]]
                points_y = [upper_y[0][k],lower_y[0][(k + 1) % number_polygon_edges], upper_y[0][(k + 1) % number_polygon_edges]]

                hinge_x = [upper_x[1][k] + upper_x[0][k], lower_x[0][(k + 1) % number_polygon_edges] * (1+ wall_fraction), upper_x[2][(k) % number_polygon_edges] + upper_x[0][(k + 1) % number_polygon_edges]]
                hinge_y = [upper_y[1][k] + upper_y[0][k], lower_y[0][(k + 1) % number_polygon_edges] * (1+ wall_fraction), upper_y[2][(k) % number_polygon_edges] + upper_y[0][(k + 1) % number_polygon_edges]]

            middle_kresling = param_Kresling(radius, points_x, points_y, points_z)
            inner_kresling = param_Kresling(radius - hinge_thickness, points_x, points_y, points_z)
            outer_kresling = param_Kresling(radius, hinge_x, hinge_y, points_z)

            #Loft between Kresling faces, create bodies from loft features
            inner_loft = add_loft(lofts,[middle_kresling, inner_kresling]) 
            inner_bodies = inner_loft.bodies.item(0)
            body_list.append(inner_bodies)

            #Loft between Kresling faces, create bodies from loft features
            outer_loft = add_loft(lofts,[middle_kresling, outer_kresling]) 
            outer_bodies = outer_loft.bodies.item(0)
            body_list.append(outer_bodies)

            if chamber_length > 0:
                outer_center_kresling = param_Kresling((radius - chamber_length), points_x, points_y, points_z)
                inner_center_kresling = param_Kresling((radius - chamber_length) - wall_thickness, points_x, points_y, points_z)
                  
                center_loft = add_loft(lofts,[inner_center_kresling, outer_center_kresling])
                center_bodies = center_loft.bodies.item(0)
                body_list.append(center_bodies)

                make_chambers(lofts,number_polygon_edges, radius-hinge_thickness, radius - chamber_length, top_rotation_angle, height, lower_x, lower_y, upper_x, upper_y)

    if base_thickness > 0:
        make_base(lower_x[0], lower_y[0], radius + wall_thickness, 0, -base_thickness, lofts, body_list)

    if lip_thickness > 0:
        make_base(upper_x[0], upper_y[0], radius - hinge_thickness, height, lip_thickness, lofts, body_list)
        make_base(upper_x[0], upper_y[0], radius + wall_thickness, height, lip_thickness, lofts, body_list)

    return body_list

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

# Make Kresling structure
Kresling = make_Kresling_body(loftFeats, radius, wall_thickness, hinge_thickness, number_polygon_edges, height, top_rotation_angle * (math.pi/180), base_thickness, lip_thickness)

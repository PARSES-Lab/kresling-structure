'''
Kris Dorsey, Sonia Roberts, and Ash Wu
K.Dorsey@Northeastern.edu
Kristen@Kristendorsey.com
This script is run from Autodesk Fusion 360 scripts and add ons interface
The sizing and equations come from Kaufman and Li 2021
Mapping from Kaufman to variables here
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
edge_length = 2.5
height = 2.5
number_polygon_edges = 6 
top_rotation_angle = 12 
wall_thickness = 0.1 

#Kresling ratios
hinge_proportion = 0.05
ratio_hinge_to_wall = 0.5
ratio_base_to_wall = 0

#Calculate hinge and base thicknesses from ratios
hinge_thickness = wall_thickness * ratio_hinge_to_wall
base_thickness = wall_thickness * ratio_base_to_wall

radius = edge_length * (2 * math.sin( math.pi / number_polygon_edges ))

def generate_polygon_points(number_of_kresling_edges, offset_angle, sine_rotation):
    polygon_points = \
        [math.cos((2 * k * math.pi / number_of_kresling_edges) - offset_angle - sine_rotation) \
        for k in range(number_of_kresling_edges)]
	
    return polygon_points 

def generate_hinge_points(number_of_kresling_edges, offset_angle, sine_rotation, hinge_proportion):
    half_inner_angle = math.pi / number_of_kresling_edges

    polygon_points = [math.cos((2 * k * math.pi / number_of_kresling_edges) - (offset_angle + sine_rotation)) for k in range(number_of_kresling_edges)]

    #changed to +shift_angle over -shift_angle to fix sign issue
    gen_hinge_points = [math.sin((2 * item + 1) * half_inner_angle - sine_rotation - offset_angle) for item in range(number_of_kresling_edges)]

    hinge_points_close = [(polygon_points[item] - (hinge_proportion) * gen_hinge_points[item]) for item in range(number_of_kresling_edges)]
    hinge_points_far = [(polygon_points[item] - (1-hinge_proportion) * gen_hinge_points[item]) for item in range(number_of_kresling_edges)]
    
    return hinge_points_close + hinge_points_far

def find_intersection_points(number_of_kresling_edges, offset_angle, height, hinge_points_x, hinge_points_y, hinge_proportion, upper_level):
    #find the parameter intersection of the parallel lines with the two hinge points
    #This is not a generalized function yet, it only works for calculating top point
    half_inner_angle = math.pi / number_of_kresling_edges

    intersection_point_x = []
    intersection_point_y = []
    intersection_point_z = []

    if upper_level == 0:
        for item in range(number_of_kresling_edges):

            parameter_numerator = math.sin((2 * item + 1) * half_inner_angle) * (2 * hinge_proportion - 1)
            parameter_denominator =  math.cos(2 * (item + 1) * half_inner_angle) - math.cos(2 * item * half_inner_angle)
            parameter = parameter_numerator / parameter_denominator

            intersection_point_x.append(parameter * (math.cos(2 * item * half_inner_angle - offset_angle) - math.cos(2 * item * half_inner_angle)) + hinge_points_x[item])
            intersection_point_y.append(parameter * (math.sin(2 * item * half_inner_angle - offset_angle) - math.sin(2 * item * half_inner_angle)) + hinge_points_y[item])
            intersection_point_z.append(parameter * height)
    else:
        for item in range(number_of_kresling_edges):

            parameter_numerator = math.sin((2 * item + 1) * half_inner_angle - offset_angle) * (2 * hinge_proportion - 1)
            parameter_denominator =  math.cos(2 * (item + 1) * half_inner_angle - offset_angle) - math.cos(2 * item * half_inner_angle - offset_angle)
            parameter = parameter_numerator / parameter_denominator

            intersection_point_x.append(parameter * (-math.cos(2 * item * half_inner_angle - offset_angle) + math.cos(2 * (item + 1) * half_inner_angle)) + hinge_points_x[item])
            intersection_point_y.append(parameter * (-math.sin(2 * item * half_inner_angle - offset_angle) + math.sin(2 * (item + 1) * half_inner_angle)) + hinge_points_y[item])
            intersection_point_z.append(parameter * -height + height)
    
    intersection_points = [intersection_point_x, intersection_point_y, intersection_point_z]
    return intersection_points

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

def add_loft_feature(loft_features,profile_obj_array):
    #Lofts objects from sketch profiles
    loft_input = loft_features.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    loft0 = loft_input.loftSections
    for x in profile_obj_array:
        loft0.add(x)
    loft_input.isSolid = True 
    loft_output = loft_features.add(loft_input)
    return loft_output

def make_base(lower_x_points, lower_y_points, thickness, lofts, body_list):

    #Take bottom exterior points and create two drawings at spacing t from each other
    lid_lower_points = gen_sketch(lower_x_points, lower_y_points, [-thickness for k in range(len(lower_x_points))])
    lid_upper_points = gen_sketch(lower_x_points, lower_y_points, [0 for k in range(len(lower_x_points))])

    #Loft between lower Kresling polygon and upper Kresling polygon
    loft_lid = add_loft_feature(lofts,[lid_lower_points,lid_upper_points])
    
    body_K_lid = loft_lid.bodies.item(0)
    body_list.append(body_K_lid) 
    return body_list

def param_Kresling(radius, points_x, points_y, points_z):
    #Multiply all points by radius
    points_x_parameterized = [i * radius for i in points_x]
    points_y_parameterized = [i * radius for i in points_y]

    #Make the Kresling triangle drawing
    Kresling_profile = gen_sketch(points_x_parameterized, points_y_parameterized, points_z)
    return Kresling_profile

def make_Kresling_body(lofts, radius, wall_thickness, hinge_thickness, number_polygon_edges, height, top_rotation_angle, base_thickness,hinge_proportion):
    #Create each Kresling triangle according to specified dimensions

    body_list = [] #Make an empty body list to append new bodies to

    #Create point lists for Kresling triangle points
    lower_x = generate_polygon_points(number_polygon_edges, 0, 0)
    upper_x = generate_polygon_points(number_polygon_edges, top_rotation_angle, 0)
    lower_y = generate_polygon_points(number_polygon_edges, 0, math.pi/2)
    upper_y = generate_polygon_points(number_polygon_edges, top_rotation_angle, math.pi/2)

    lower_hinge_x = generate_hinge_points(number_polygon_edges, 0, 0, hinge_proportion)
    upper_hinge_x = generate_hinge_points(number_polygon_edges, top_rotation_angle, 0, hinge_proportion)
    lower_hinge_y = generate_hinge_points(number_polygon_edges, 0, math.pi/2, hinge_proportion)
    upper_hinge_y = generate_hinge_points(number_polygon_edges, top_rotation_angle, math.pi/2, hinge_proportion)

    intersection_points_lower = find_intersection_points(number_polygon_edges, top_rotation_angle, height, lower_hinge_x, lower_hinge_y, hinge_proportion, 0)
    intersection_lower_x = intersection_points_lower[0]
    intersection_lower_y = intersection_points_lower[1]
    intersection_lower_z = intersection_points_lower[2]

    intersection_points_upper = find_intersection_points(number_polygon_edges, top_rotation_angle, height, upper_hinge_x, upper_hinge_y, hinge_proportion, 1)
    intersection_upper_x = intersection_points_upper[0]
    intersection_upper_y = intersection_points_upper[1]
    intersection_upper_z = intersection_points_upper[2]

    #Draw upper and lower Kresling triangles from point lists
    for m in range(2):    
        for k in range(6):#number_polygon_edges):

            if m == 0: #make upper or lower triangle, m == 0 is lower

                points_z = [0, height, 0]
                points_x = [lower_x[k], upper_x[k], lower_x[(k + 1) % number_polygon_edges]]
                points_y = [lower_y[k], upper_y[k], lower_y[(k + 1) % number_polygon_edges]]
                
                points_hinge_x = [lower_hinge_x[(k) % len(lower_hinge_x)], intersection_lower_x[(k) % len(intersection_lower_x)], lower_hinge_x[(number_polygon_edges + k) % len(lower_hinge_x)]]
                points_hinge_y = [lower_hinge_y[(k) % len(lower_hinge_x)], intersection_lower_y[(k) % len(intersection_lower_x)], lower_hinge_y[(number_polygon_edges + k) % len(lower_hinge_x)]]
                points_hinge_z = [0, intersection_lower_z[k], 0]
        
            else:
                points_z = [height, 0, height]
                points_x = [upper_x[k],lower_x[(k + 1) % number_polygon_edges], upper_x[(k + 1) % number_polygon_edges]]
                points_y = [upper_y[k],lower_y[(k + 1) % number_polygon_edges], upper_y[(k + 1) % number_polygon_edges]]

                points_hinge_x = [upper_hinge_x[(k) % len(lower_hinge_x)], intersection_upper_x[(k) % len(intersection_upper_x)], upper_hinge_x[(number_polygon_edges + k) % len(lower_hinge_x)]]
                points_hinge_y = [upper_hinge_y[(k) % len(lower_hinge_x)], intersection_upper_y[(k) % len(intersection_upper_x)], upper_hinge_y[(number_polygon_edges + k) % len(lower_hinge_x)]]
                points_hinge_z = [height, intersection_upper_z[k % len(intersection_upper_z)], height]
            
            #Make the Kresling triangles
            outer_kresling = param_Kresling(radius, points_x, points_y, points_z)
            center_kresling = param_Kresling(radius - hinge_thickness, points_x, points_y, points_z)

            #Loft between interior and exterior Kresling faces, create bodies from loft features
            outer_loft = add_loft_feature(lofts,[outer_kresling,center_kresling]) 
            outer_bodies = outer_loft.bodies.item(0)
            body_list.append(outer_bodies)

            
            if hinge_thickness < wall_thickness: 
                inner_kresling = param_Kresling(radius - wall_thickness, points_hinge_x, points_hinge_y, points_hinge_z)
                inner_loft = add_loft_feature(lofts,[inner_kresling, center_kresling]) 
                inner_bodies = inner_loft.bodies.item(0)
                body_list.append(inner_bodies)
            
            
    if base_thickness > 0:
        make_base([i * radius for i in lower_x],[i * radius for i in lower_y], base_thickness, lofts, body_list)

    '''
    #Generalized sketch from point list in X, Y, Z
    new_sketch = sketchObjs.add(rootComp.xYConstructionPlane)

    #define a shape two points at a time
    Kres_lines = new_sketch.sketchCurves.sketchLines

    point0 = adsk.core.Point3D.create(0, 0, 0)
    point1 = adsk.core.Point3D.create(radius * lower_x[0], radius * lower_y[0], 0)
    Kres_lines.addByTwoPoints(point0, point1)

    point1 = adsk.core.Point3D.create(radius * lower_x[2], radius * lower_y[2], 0)
    Kres_lines.addByTwoPoints(point0, point1)
    
    point1 = adsk.core.Point3D.create(radius * lower_x[4], radius * lower_y[4], 0)
    Kres_lines.addByTwoPoints(point0, point1)
    '''
    
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
Kresling = make_Kresling_body(loftFeats, edge_length, wall_thickness, hinge_thickness, number_polygon_edges, height , top_rotation_angle * (math.pi/180), base_thickness,hinge_proportion)

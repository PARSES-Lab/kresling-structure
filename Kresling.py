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
number_polygon_edges = 6 
hinge_thickness = 0.125
lamb = 0.75
tube_OD = 0.5
height_compressed = 1
wall_thickness = 0
chamber_length = 0

#Calculate hinge and base thicknesses from ratios (do not change these values)
#hinge_thickness = wall_thickness * ratio_hinge_to_wall
ratio_base_to_wall = 1
ratio_lip_to_wall = 0

#calculate Kresling dimensions from parameters above
radius = edge_length * (2 * math.sin( math.pi / number_polygon_edges ))
half_inner_angle = math.pi / number_polygon_edges
top_rotation_angle_compressed = 2*lamb*(math.pi/2 - half_inner_angle)
top_rotation_angle = 2*(1-lamb)*(math.pi/2 - half_inner_angle)
height = math.sqrt(height_compressed**2 + 2*radius**2*(math.cos(top_rotation_angle + 2*half_inner_angle) - math.cos(top_rotation_angle_compressed + 2*half_inner_angle)))

min_rad = math.sqrt((height**2-height_compressed**2)/(2*(math.cos(2*half_inner_angle) - math.cos(top_rotation_angle_compressed + 2*half_inner_angle)))) +0.1

'''
#problem here is that chamber radius is high to get rotation and compression. 
if (min_rad > (radius - chamber_length)):
    chamber_length = 0 
else:
    top_rotation_angle_chamber = math.acos(((height**2-height_compressed**2)/2/(radius -chamber_length)**2+math.cos(top_rotation_angle_compressed + 2*half_inner_angle)))-2*half_inner_angle
'''

base_thickness = (wall_thickness + hinge_thickness) * ratio_base_to_wall
lip_thickness = (wall_thickness + hinge_thickness) * ratio_lip_to_wall

#general purpose functions to generate Kresling points, sketches, and lofts

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

def make_base(upper_x_points, upper_y_points, radius, height, thickness, lofts, body_list, tube_OD):

    #Take exterior points and create two drawings at spacing t from each other
    lip_lower_points = gen_sketch([i * radius for i in upper_x_points], [i * radius for i in upper_y_points], [height for k in range(len(upper_x_points))])
    lip_upper_points = gen_sketch([i * radius for i in upper_x_points], [i * radius for i in upper_y_points], [height + thickness for k in range(len(upper_x_points))])

    #Loft between two drawings to make base
    loft_lip = add_loft(lofts,[lip_lower_points,lip_upper_points])
    body_K_lip = loft_lip.bodies.item(0)
    body_list.append(body_K_lip) 
    
    #Add holes for tubing
    if tube_OD > 0: 
        circle_sketch = sketchObjs.add(rootComp.xYConstructionPlane)
        circles = circle_sketch.sketchCurves.sketchCircles
        circles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), tube_OD/2)
        for circle_count in range(3):
            circles.addByCenterRadius(adsk.core.Point3D.create(radius/2 * math.cos(math.pi/2 + 2*circle_count*math.pi/3),radius/2 * math.sin(math.pi/2 + 2*circle_count*math.pi/3),0), tube_OD/2)
        
        # Extrude holes for tubing.	
        for circle_count in range(4):
            extInput = extrudeFeats.createInput(circle_sketch.profiles.item(circle_count), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            distance = adsk.core.ValueInput.createByReal(thickness)
            extInput.setDistanceExtent(False, distance)
            ext = extrudeFeats.add(extInput)
    
    return body_list

#chamber generation functions

def make_chamber_points(outer_radius, second_radius, inner_radius, first_pts, second_pts, angle_count, half_inner_angle, first_rot_angle, second_rot_angle, sine_rotation):
    #Take in chamber parameters and output the points to either side of the corner to loft between
    points_1st = \
        [outer_radius * first_pts[((angle_count) % number_polygon_edges)] - (outer_radius - wall_thickness / 2) * math.sin((((angle_count) % number_polygon_edges)*2 + 1) * half_inner_angle- first_rot_angle - sine_rotation), \
        second_radius * second_pts[((angle_count) % number_polygon_edges)] - (second_radius - wall_thickness / 2) * math.sin((((angle_count) % number_polygon_edges)*2 + 1) * half_inner_angle - second_rot_angle - sine_rotation), \
        inner_radius * first_pts[((angle_count) % number_polygon_edges)] - (inner_radius - wall_thickness / 2) * math.sin((((angle_count) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle - sine_rotation)]

    points_2nd = \
        [outer_radius * first_pts[((angle_count + 1) % number_polygon_edges)] - (wall_thickness / 2) * math.sin((((angle_count + 1) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle - sine_rotation) , \
        second_radius * second_pts[((angle_count + 1) % number_polygon_edges)] - (wall_thickness / 2) * math.sin((((angle_count + 1) % number_polygon_edges)*2 + 1) * half_inner_angle - second_rot_angle - sine_rotation), \
        inner_radius * first_pts[((angle_count + 1) % number_polygon_edges)] - (wall_thickness / 2) * math.sin((((angle_count + 1) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle - sine_rotation)]
    return [points_1st, points_2nd]

def make_chamber_walls(lofts, number_chambers, outer_radius, inner_radius, first_x, second_x, first_y, second_y, points_z, first_rot_angle, second_rot_angle, half_inner_angle, body_list):
    #loft between anchor points to either side of the Kresling polygon corners
    for item in range(number_chambers):
        angle_count = (2 * item + number_polygon_edges - 1) 

        if first_rot_angle == 0: #set whether the second radius is outer or inner depending on if it's top or bottom triangle
            second_radius = inner_radius
        else:
            second_radius = outer_radius

        points_x = make_chamber_points(outer_radius, second_radius, inner_radius, first_x, second_x, angle_count, half_inner_angle, first_rot_angle, second_rot_angle, 0)
        points_y = make_chamber_points(outer_radius, second_radius, inner_radius, first_y, second_y, angle_count, half_inner_angle, first_rot_angle, second_rot_angle, math.pi/2)

        inner_triangle = param_Kresling(1, points_x[0], points_y[0], points_z)
        outer_triangle = param_Kresling(1, points_x[1], points_y[1], points_z)

        lower_loft = add_loft(lofts,[inner_triangle,outer_triangle])
        lower_bodies = lower_loft.bodies.item(0)
        body_list.append(lower_bodies)
    return body_list 

def make_chambers(lofts, number_polygon_edges, outer_radius, inner_radius, top_rotation_angle, height, lower_x, lower_y, upper_x, upper_y):
    body_list = []
    number_chambers  = number_polygon_edges // 2
    half_inner_angle = math.pi / number_polygon_edges

    body_list = make_chamber_walls(lofts, number_chambers, outer_radius, inner_radius, lower_x, upper_x, lower_y, upper_y, [0, height, 0], 0, top_rotation_angle, half_inner_angle, body_list)
    body_list = make_chamber_walls(lofts, number_chambers, outer_radius, inner_radius, upper_x, lower_x, upper_y, lower_y, [height, 0, height], top_rotation_angle, 0, half_inner_angle, body_list)
    return body_list


def make_Kresling_body(lofts, radius, wall_thickness, hinge_thickness, number_polygon_edges, height, top_rotation_angle, base_thickness, lip_thickness, tube_OD):
    #Create each Kresling triangle according to specified dimensions

    body_list = [] #Make an empty body list to append new bodies to

    wall_fraction = wall_thickness / radius
    #Create Kresling and hinge point lists for Kresling triangle points
    lower_x = generate_polygon_points(number_polygon_edges, wall_fraction, 0, 0)
    upper_x = generate_polygon_points(number_polygon_edges, wall_fraction, top_rotation_angle, 0)
    lower_y = generate_polygon_points(number_polygon_edges, wall_fraction, 0, math.pi/2)
    upper_y = generate_polygon_points(number_polygon_edges, wall_fraction, top_rotation_angle, math.pi/2)
 
    #Draw upper and lower Kresling triangles from point lists
    for m in range(2):    
        for k in range(number_polygon_edges):

            if m == 0: #make upper or lower triangle, m == 0 is base of triangle at z = 0 (lower)

                points_z = [0, height, 0]
                points_x = [lower_x[0][k], upper_x[0][k], lower_x[0][(k + 1) % number_polygon_edges]]
                points_y = [lower_y[0][k], upper_y[0][k], lower_y[0][(k + 1) % number_polygon_edges]]

                hinge_x = [lower_x[1][k] + lower_x[0][k], upper_x[0][k] * (1+ wall_fraction), lower_x[2][(k) % number_polygon_edges] + lower_x[0][(k + 1) % number_polygon_edges]]
                hinge_y = [lower_y[1][k] + lower_y[0][k], upper_y[0][k] * (1+ wall_fraction), lower_y[2][(k) % number_polygon_edges] + lower_y[0][(k + 1) % number_polygon_edges]]
        
            else:
                points_z = [height, 0, height]
                points_x = [upper_x[0][k],lower_x[0][(k + 1) % number_polygon_edges], upper_x[0][(k + 1) % number_polygon_edges]]
                points_y = [upper_y[0][k],lower_y[0][(k + 1) % number_polygon_edges], upper_y[0][(k + 1) % number_polygon_edges]]

                hinge_x = [upper_x[1][k] + upper_x[0][k], lower_x[0][(k + 1) % number_polygon_edges] * (1+ wall_fraction), upper_x[2][(k) % number_polygon_edges] + upper_x[0][(k + 1) % number_polygon_edges]]
                hinge_y = [upper_y[1][k] + upper_y[0][k], lower_y[0][(k + 1) % number_polygon_edges] * (1+ wall_fraction), upper_y[2][(k) % number_polygon_edges] + upper_y[0][(k + 1) % number_polygon_edges]]

            middle_kresling = param_Kresling(radius - wall_thickness, points_x, points_y, points_z)
            inner_kresling = param_Kresling(radius - hinge_thickness - wall_thickness, points_x, points_y, points_z)
            
            #Loft between Kresling faces, create bodies from loft features
            inner_loft = add_loft(lofts,[middle_kresling, inner_kresling]) 
            inner_bodies = inner_loft.bodies.item(0)
            body_list.append(inner_bodies)

            if wall_thickness > 0: 
                #Loft between Kresling faces, create bodies from loft features
                outer_kresling = param_Kresling(radius - wall_thickness, hinge_x, hinge_y, points_z)
                outer_loft = add_loft(lofts,[middle_kresling, outer_kresling]) 
                outer_bodies = outer_loft.bodies.item(0)
                body_list.append(outer_bodies)

            if chamber_length > 0:
                outer_center_kresling = param_Kresling((radius - chamber_length), points_x, points_y, points_z)
                inner_center_kresling = param_Kresling((radius - chamber_length) - hinge_thickness, points_x, points_y, points_z)
                  
                center_loft = add_loft(lofts,[inner_center_kresling, outer_center_kresling])
                center_bodies = center_loft.bodies.item(0)
                body_list.append(center_bodies)
    
    if chamber_length > 0:
            make_chambers(lofts,number_polygon_edges, radius - hinge_thickness - wall_thickness, radius - chamber_length, top_rotation_angle, height, lower_x[0], lower_y[0], upper_x[0], upper_y[0])

    if base_thickness > 0:
        make_base(lower_x[0], lower_y[0], radius, 0, -base_thickness, lofts, body_list, tube_OD)

    if lip_thickness > 0:
        make_base(upper_x[0], upper_y[0], radius, height, lip_thickness, lofts, body_list)
        make_base(upper_x[0], upper_y[0], radius - hinge_thickness - wall_thickness, height, lip_thickness, lofts, body_list)
       
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
extrudeFeats = rootComp.features.extrudeFeatures

# Make Kresling structure
Kresling = make_Kresling_body(loftFeats, radius, wall_thickness, hinge_thickness, number_polygon_edges, height, top_rotation_angle, base_thickness, lip_thickness, tube_OD)

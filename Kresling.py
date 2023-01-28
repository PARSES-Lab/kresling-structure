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
top_rotation_angle = 31 # in degrees 
wall_thickness = 0.14 
chamber_length = 1.5

#Ratios to hack the Kresling to increase compliance
#Values for a standard Kresling with two lids are
# Ratio of wall length of where the hinge angle intersects with polygon. For example, 0.1 draws the hinge point starting at 10% and 90% across the polygon
#hinge_proportion = 0.05

#Hinge to wall is the hinge thickness ratio, relative to specified wall thickness
#ratio_hinge_to_wall = 1

#Base to wall is the lower base thickess ratio
#ratio_base_to_wall = 1

#Lip to wall is the upper lip thickness ratio (that upper lid sits within)
#ratio_lip_to_wall = 1

hinge_proportion = 0

#temporary hinge definition using offset instead of proportion:
hinge_offset = 0.1

#generate hinges on the inside faces of the Kresling if true, otherwise generate on the outside
inside_hinges = True

ratio_hinge_to_wall = 0.9
ratio_base_to_wall = 1
ratio_lip_to_wall = 1

#Calculate hinge and base thicknesses from ratios (do not change these values)
hinge_thickness = wall_thickness * ratio_hinge_to_wall
base_thickness = wall_thickness * ratio_base_to_wall
lip_thickness = wall_thickness * ratio_lip_to_wall

radius = edge_length * (2 * math.sin( math.pi / number_polygon_edges ))

def generate_polygon_points(number_of_kresling_edges, offset_angle, sine_rotation):
    polygon_points = \
        [math.cos((2 * k * math.pi / number_of_kresling_edges) - offset_angle - sine_rotation) \
        for k in range(number_of_kresling_edges)]
	
    return polygon_points 

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

def add_loft(loft_features,profile_obj_array):
    #Lofts objects from sketch profiles
    loft_input = loft_features.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    loft0 = loft_input.loftSections
    for x in profile_obj_array:
        loft0.add(x)
    loft_input.isSolid = True 
    loft_output = loft_features.add(loft_input)
    return loft_output

def make_base(upper_x_points, upper_y_points, radius, height, thickness, lofts, body_list):

    #Take exterior points and create two drawings at spacing t from each other
    lip_lower_points = gen_sketch([i * radius for i in upper_x_points], [i * radius for i in upper_y_points], [height for k in range(len(upper_x_points))])
    lip_upper_points = gen_sketch([i * radius for i in upper_x_points], [i * radius for i in upper_y_points], [height + thickness for k in range(len(upper_x_points))])

    #Loft between two drawings to make base
    loft_lip = add_loft(lofts,[lip_lower_points,lip_upper_points])
    
    body_K_lip = loft_lip.bodies.item(0)
    body_list.append(body_K_lip) 

    
    if thickness > 0: 
        #Take exterior points and create two drawings at spacing t from each other
        lip_lower_points = gen_sketch([i * (radius - thickness) for i in upper_x_points], [i * (radius - thickness) for i in upper_y_points], [height for k in range(len(upper_x_points))])
        lip_upper_points = gen_sketch([i * (radius - thickness) for i in upper_x_points], [i * (radius - thickness) for i in upper_y_points], [height + thickness for k in range(len(upper_x_points))])

        #Loft between two drawings to make base
        loft_lip2 = add_loft(lofts,[lip_lower_points,lip_upper_points])
    
        body_K_lip2 = loft_lip2.bodies.item(0)
        body_list.append(body_K_lip2) 
    
    return body_list

def make_chambers(lofts, number_polygon_edges, outer_radius, inner_radius, top_rotation_angle, height, lower_x, lower_y, upper_x, upper_y):
    body_list = []
    number_chambers  = number_polygon_edges // 2
    half_inner_angle = math.pi / number_polygon_edges

    body_list = make_chamber_walls(lofts, number_chambers, outer_radius, inner_radius, lower_x, upper_x, lower_y, upper_y, [0, height, 0], 0, top_rotation_angle, half_inner_angle, body_list)
    body_list = make_chamber_walls(lofts, number_chambers, outer_radius, inner_radius, upper_x, lower_x, upper_y, lower_y, [height, 0, height], top_rotation_angle, 0, half_inner_angle, body_list)
    return body_list

def make_chamber_walls(lofts, number_chambers, outer_radius, inner_radius, first_x, second_x, first_y, second_y, points_z, first_rot_angle, second_rot_angle, half_inner_angle, body_list):
    for item in range(number_chambers):
        angle_count = (item * 2 + number_polygon_edges - 1) 

        if first_rot_angle == 0: #set whether the second radius is outer or inner depending on if it's top or bottom triangle
            second_radius = inner_radius
        else:
            second_radius = outer_radius

        points_x = make_chamber_points(outer_radius, second_radius, inner_radius, first_x, second_x, angle_count, half_inner_angle, first_rot_angle, second_rot_angle, 0)
        points_y = make_chamber_points(outer_radius, second_radius, inner_radius, first_y, second_y, angle_count, half_inner_angle, first_rot_angle, second_rot_angle, -math.pi/2)

        inner_triangle = param_Kresling(1, points_x[0], points_y[0], points_z)
        outer_triangle = param_Kresling(1, points_x[1], points_y[1], points_z)

        lower_loft = add_loft(lofts,[inner_triangle,outer_triangle])
        lower_bodies = lower_loft.bodies.item(0)
        body_list.append(lower_bodies)
    return body_list 

def make_chamber_points(outer_radius, second_radius, inner_radius, first_pts, second_pts, angle_count, half_inner_angle, first_rot_angle, second_rot_angle, sine_rotation):
    points_1st = \
        [outer_radius * first_pts[((angle_count) % number_polygon_edges)] - (outer_radius - wall_thickness / 2) * math.sin((((angle_count) % number_polygon_edges)*2 + 1) * half_inner_angle- first_rot_angle + sine_rotation), \
        second_radius * second_pts[((angle_count) % number_polygon_edges)] - (second_radius - wall_thickness / 2) * math.sin((((angle_count) % number_polygon_edges)*2 + 1) * half_inner_angle - second_rot_angle + sine_rotation), \
        inner_radius * first_pts[((angle_count) % number_polygon_edges)] - (inner_radius - wall_thickness / 2) * math.sin((((angle_count) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle + sine_rotation)]

    points_2nd = \
        [outer_radius * first_pts[((angle_count + 1) % number_polygon_edges)] - (wall_thickness / 2) * math.sin((((angle_count + 1) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle + sine_rotation) , \
        second_radius * second_pts[((angle_count + 1) % number_polygon_edges)] - (wall_thickness / 2) * math.sin((((angle_count + 1) % number_polygon_edges)*2 + 1) * half_inner_angle - second_rot_angle + sine_rotation), \
        inner_radius * first_pts[((angle_count + 1) % number_polygon_edges)] - (wall_thickness / 2) * math.sin((((angle_count + 1) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle + sine_rotation)]
    return [points_1st, points_2nd]

def make_chamber_walls_bak(lofts, number_chambers, outer_radius, inner_radius, first_x, second_x, first_y, second_y, points_z, first_rot_angle, second_rot_angle, half_inner_angle, body_list):
    for item in range(number_chambers):
        angle_count = (item * 2 + number_polygon_edges - 1) 

        if first_rot_angle == 0: #set whether the second radius is outer or inner depending on if it's top or bottom triangle
            second_radius = inner_radius
        else:
            second_radius = outer_radius

        points_x_1st = \
            [outer_radius * first_x[((angle_count) % number_polygon_edges)] - (outer_radius - wall_thickness / 2) * math.sin((((angle_count) % number_polygon_edges)*2 + 1) * half_inner_angle- first_rot_angle), \
            second_radius * second_x[((angle_count) % number_polygon_edges)] - (second_radius - wall_thickness / 2) * math.sin((((angle_count) % number_polygon_edges)*2 + 1) * half_inner_angle - second_rot_angle), \
            inner_radius * first_x[((angle_count) % number_polygon_edges)] - (inner_radius - wall_thickness / 2) * math.sin((((angle_count) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle)]

        points_x_2nd = \
            [outer_radius * first_x[((angle_count + 1) % number_polygon_edges)] - (wall_thickness / 2) * math.sin((((angle_count + 1) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle) , \
            second_radius * second_x[((angle_count + 1) % number_polygon_edges)] - (wall_thickness / 2) * math.sin((((angle_count + 1) % number_polygon_edges)*2 + 1) * half_inner_angle - second_rot_angle), \
            inner_radius * first_x[((angle_count + 1) % number_polygon_edges)] - (wall_thickness / 2) * math.sin((((angle_count + 1) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle)]
        
        points_y_1st = \
            [outer_radius * first_y[((angle_count) % number_polygon_edges)] + (outer_radius - wall_thickness / 2) * math.cos((((angle_count) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle), \
            second_radius * second_y[((angle_count) % number_polygon_edges)] + (second_radius - wall_thickness / 2) * math.cos((((angle_count) % number_polygon_edges)*2 + 1) * half_inner_angle - second_rot_angle), \
            inner_radius * first_y[((angle_count) % number_polygon_edges)] + (inner_radius - wall_thickness / 2) * math.cos((((angle_count) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle)]

        points_y_2nd = \
            [outer_radius * first_y[((angle_count + 1) % number_polygon_edges)] + (wall_thickness / 2) * math.cos((((angle_count + 1) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle), \
            second_radius * second_y[((angle_count + 1) % number_polygon_edges)] + (wall_thickness / 2) * math.cos((((angle_count + 1) % number_polygon_edges)*2 + 1) * half_inner_angle - second_rot_angle), \
            inner_radius * first_y[((angle_count + 1) % number_polygon_edges)] + (wall_thickness / 2) * math.cos((((angle_count + 1) % number_polygon_edges)*2 + 1) * half_inner_angle - first_rot_angle)]

        inner_triangle = param_Kresling(1, points_x_1st, points_y_1st, points_z)
        outer_triangle = param_Kresling(1, points_x_2nd, points_y_2nd, points_z)

        lower_loft = add_loft(lofts,[inner_triangle,outer_triangle])
        lower_bodies = lower_loft.bodies.item(0)
        body_list.append(lower_bodies)
    return body_list 

def param_Kresling(radius, points_x, points_y, points_z):
    #Multiply all points by radius
    points_x_parameterized = [i * radius for i in points_x]
    points_y_parameterized = [i * radius for i in points_y]

    #Make the Kresling triangle drawing
    Kresling_profile = gen_sketch(points_x_parameterized, points_y_parameterized, points_z)
    return Kresling_profile

def cut_combine(target_body, tool_body):
    #Cut the tool body out of the target body and discard tool body
    tools = adsk.core.ObjectCollection.create()
    tools.add(tool_body)
    combine_input: adsk.fusion.CombineFeatureInput = combineFeats.createInput(target_body, tools)
    combine_input.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    return combineFeats.add(combine_input)

def construct_offset_plane(plane_profile, offset_distance):
    #create planes input
    plane_input = cPlaneObjs.createInput()

    #set offset distance
    offset_value = adsk.core.ValueInput.createByReal(offset_distance)
    plane_input.setByOffset(plane_profile, offset_value)

    #create the offset construction plane
    offset_plane = cPlaneObjs.add(plane_input)

    return offset_plane

def project_sketch(input_sketch,working_plane):
    #Make new sketch on the working plane
    projected_sketch = sketchObjs.add(working_plane)

    #Project curves of input sketch onto the working plane
    for curve in input_sketch.sketchCurves:
        projected_sketch.project(curve)
 
    return projected_sketch

def offset_sketch_inside(input_sketch, offset_distance):
    #Find all geometry to be offset
    offset_geometry = adsk.core.ObjectCollection.create()
    input_lines = input_sketch.sketchCurves.sketchLines
    offset_geometry.clear()
    [offset_geometry.add(line) for line in input_lines]

    #Keep track of original sketches
    original_sketch_count = input_sketch.sketchCurves.sketchLines.count

    #Define offset direction by picking a point in the center of the geometry
    #Average the coordinate locations of all the sketch points in the geometry
    x_tot = 0
    y_tot = 0
    z_tot = 0
    for point in input_sketch.sketchPoints:
        x_tot += point.geometry.x
        y_tot += point.geometry.y
        z_tot += point.geometry.z
    total_points = input_sketch.sketchPoints.count
    x_dir = x_tot / total_points
    y_dir = y_tot / total_points
    z_dir = z_tot / total_points
    
    offset_dir = adsk.core.Point3D.create(x_dir,y_dir,z_dir)

    #Make original lines construction lines
    for i in range(original_sketch_count):
        input_sketch.sketchCurves.sketchLines.item(i).isConstruction = True

    #Offset sketch inwards by specified distance
    input_sketch.offset(offset_geometry, offset_dir, offset_distance)
    
    return

def create_hinge_extrude(original_sketch, offset_from_original, hinge_loft_thickness, upper_or_lower):
    #Get profile of original Kresling triangle sketch
    original_profile = original_sketch.profiles.item(0)

    #Create construction plane by offsetting the original profile by the hinge thickness
    if upper_or_lower == 0: #0 is lower
        hinge_plane_offset = hinge_loft_thickness
    else:
        hinge_plane_offset = hinge_loft_thickness * (-1) #if a hinge is being generated on an upper plane, the offset must be reversed
    
    hinge_plane = construct_offset_plane(original_profile, hinge_plane_offset)

    #Project the original sketch onto the construction plane in a new sketch
    hinge_sketch = project_sketch(original_sketch, hinge_plane)
    #Offset the projection on the new sketch by however much the hinge triangle is smaller than the original
    offset_sketch_inside(hinge_sketch, offset_from_original)

    #Loft the original triangle to the hinge triangle
    hinge_profile = hinge_sketch.profiles.item(0)
    hinge_loft = add_loft(loftFeats,[original_profile, hinge_profile])

    return hinge_loft

def make_Kresling_body(lofts, radius, wall_thickness, hinge_thickness, number_polygon_edges, height, top_rotation_angle, base_thickness, lip_thickness, hinge_proportion):
    #Create each Kresling triangle according to specified dimensions

    body_list = [] #Make an empty body list to append new bodies to

    #Create point lists for Kresling triangle points
    lower_x = generate_polygon_points(number_polygon_edges, 0, 0)
    upper_x = generate_polygon_points(number_polygon_edges, top_rotation_angle, 0)
    lower_y = generate_polygon_points(number_polygon_edges, 0, math.pi/2)
    upper_y = generate_polygon_points(number_polygon_edges, top_rotation_angle, math.pi/2)

    #Draw upper and lower Kresling triangles from point lists
    for m in range(2):    
        for k in range(6):#number_polygon_edges):

            if m == 0: #make upper or lower triangle, m == 0 is lower

                points_z = [0, height, 0]
                points_x = [lower_x[k], upper_x[k], lower_x[(k + 1) % number_polygon_edges]]
                points_y = [lower_y[k], upper_y[k], lower_y[(k + 1) % number_polygon_edges]]
        
            else:
                points_z = [height, 0, height]
                points_x = [upper_x[k],lower_x[(k + 1) % number_polygon_edges], upper_x[(k + 1) % number_polygon_edges]]
                points_y = [upper_y[k],lower_y[(k + 1) % number_polygon_edges], upper_y[(k + 1) % number_polygon_edges]]
            
            outer_kresling = param_Kresling(radius - hinge_thickness, points_x, points_y, points_z)
            inner_kresling = param_Kresling(radius - wall_thickness, points_x, points_y, points_z)

            #Generate hinges on either the inside or the outside
            if inside_hinges:
                inner_kresling_sketch = inner_kresling.parentSketch
                #Flip the offset direction of the hinge plane generation based on upper or lower Kresling face
                if m == 0:
                    flip_value = 1
                elif m == 1:
                    flip_value = 0
                hinge_loft = create_hinge_extrude(inner_kresling_sketch, hinge_offset, hinge_thickness, flip_value)
            else:
                outer_kresling_sketch = outer_kresling.parentSketch
                hinge_loft = create_hinge_extrude(outer_kresling_sketch, hinge_offset, hinge_thickness, m)

            hinge_bodies = hinge_loft.bodies.item(0)
            body_list.append(hinge_bodies)

            if hinge_thickness < wall_thickness:
                #Loft between interior and exterior Kresling faces, create bodies from loft features
                outer_loft = add_loft(lofts,[outer_kresling, inner_kresling]) 
                outer_bodies = outer_loft.bodies.item(0)
                body_list.append(outer_bodies)

            if chamber_length > 0:
                outer_center_kresling = param_Kresling((radius - chamber_length), points_x, points_y, points_z)
                inner_center_kresling = param_Kresling((radius - chamber_length) - hinge_thickness, points_x, points_y, points_z)
                  
                center_loft = add_loft(lofts,[inner_center_kresling, outer_center_kresling])
                center_bodies = center_loft.bodies.item(0)
                body_list.append(center_bodies)

    make_chambers(lofts,number_polygon_edges, radius-hinge_thickness, radius - chamber_length, top_rotation_angle, height, lower_x, lower_y, upper_x, upper_y)

    if base_thickness > 0:
        make_base(lower_x, lower_y, radius, 0, -1 * wall_thickness, lofts, body_list)

    if lip_thickness > 0:
        make_base(upper_x, upper_y, radius, height, 1 * wall_thickness, lofts, body_list)
        targetTop = body_list[len(body_list)-2]
        toolTop = body_list[len(body_list)-1]
        cut_combine(targetTop, toolTop)

    return body_list

##### Main code #####

# Create Fusion document 
app = adsk.core.Application.get()
ui = app.userInterface
doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
design = app.activeProduct

# Create sketch, construction plane, loft objects, and combine objects
rootComp = design.rootComponent
sketchObjs = rootComp.sketches
cPlaneObjs = rootComp.constructionPlanes
loftFeats = rootComp.features.loftFeatures
combineFeats = rootComp.features.combineFeatures

# Make Kresling structure
Kresling = make_Kresling_body(loftFeats, radius, wall_thickness, hinge_thickness, number_polygon_edges, height, top_rotation_angle * (math.pi/180), base_thickness, lip_thickness, hinge_proportion)
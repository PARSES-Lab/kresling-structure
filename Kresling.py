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

########### BEGIN USER MODIFIED PARAMETERS ############

#Kresling dimensions 
# all in cm
edge_length = 3
number_polygon_edges = 6 
wall_thickness = 0.1
lamb = 0.75
height_compressed = 1
chamber_length = 0 #1.5

#The distance between the original Kresling triangle and the hinge Kresling triangle
hinge_offset = 0.075
#this needs to be recalculated

#Collar dimensions
collar_height = 0.55
collar_ratio = 0.25/0.55
collar_offset = wall_thickness * 2
gen_collar_holes = True
gen_symmetric_collars = True

#Generate lid if true, otherwise generate Kresling without the lid
keepLid = True
tube_OD = 0 #0.28

ratio_hinge_to_wall = 1
ratio_base_to_wall = 1
ratio_lip_to_wall = 1

########### END USER MODIFIED PARAMETERS ############

#calculate Kresling dimensions from parameters above
radius = edge_length * (2 * math.sin( math.pi / number_polygon_edges ))
half_inner_angle = math.pi / number_polygon_edges
top_rotation_angle_compressed = 2*lamb*(math.pi/2 - half_inner_angle)
top_rotation_angle = 2*(1-lamb)*(math.pi/2 - half_inner_angle)
height = math.sqrt(height_compressed**2 + 2*radius**2*(math.cos(top_rotation_angle + 2*half_inner_angle) - math.cos(top_rotation_angle_compressed + 2*half_inner_angle)))

#Calculate hinge and base thicknesses from ratios 
hinge_thickness = wall_thickness * ratio_hinge_to_wall
base_thickness = wall_thickness * ratio_base_to_wall
lip_thickness = wall_thickness * ratio_lip_to_wall

def generate_polygon_points(number_of_kresling_edges, offset_angle, sine_rotation):
    polygon_points = \
        [math.cos((2 * (k // 2) * math.pi / number_of_kresling_edges) - offset_angle * (k % 2) - sine_rotation) \
        for k in range(4)]
    
    return polygon_points

def gen_sketch(points_x, points_y, points_z):
    #Generate closed sketch from point list in X, Y, Z
    pgon_sketch = sketchObjs.add(rootComp.xYConstructionPlane)

    #define a shape two points at a time
    pgon_lines = pgon_sketch.sketchCurves.sketchLines    
    for k in range(len(points_x)):
        #Wrap around to 0th point again to enclose the polygon
        point0 = adsk.core.Point3D.create(points_x[k], points_y[k], points_z[k])
        point1 = adsk.core.Point3D.create(points_x[((k+1) % len(points_x))], points_y[((k+1) % len(points_x))], points_z[((k+1) % len(points_x))])
    
        #draw the shape by adding the line
        pgon_sketch.sketchCurves.sketchLines.addByTwoPoints(point0, point1)
    
    profile = pgon_sketch.profiles.item(0)
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

def make_base(x_points, y_points, radius, height, thickness, lofts, body_list):

    #Take exterior points and create two drawings at spacing t from each other
    base_lower = gen_sketch([i * radius for i in x_points], [i * radius for i in y_points], [height for k in range(len(x_points))])
    base_upper = gen_sketch([i * radius for i in x_points], [i * radius for i in y_points], [height + thickness for k in range(len(x_points))])

    #Loft between two drawings to make base
    base_loft = add_loft(lofts,[base_lower,base_upper])
    base_body = base_loft.bodies.item(0)
    body_list.append(base_body) 

    return base_body  

def make_collar(x_points, y_points, radius, height, thickness, collar_height, collar_ratio, collar_offset, gen_collar_holes, lofts, body_list):

    #Define the outer points of the quadrilateral of the collar
    x_coord = [i * radius for i in x_points]
    y_coord = [i * radius for i in y_points]

    ## LOWER QUADRILATERAL COORDINATES ##
    #Define z height
    z_coord_bottom = [height for k in range(4)]

    #Define the inner points of the lower quadrilateral of the collar
    distance_ratio_bottom = (radius - thickness) / radius
    x_inner_bottom = [i * distance_ratio_bottom for i in reversed(x_coord)]
    y_inner_bottom = [i * distance_ratio_bottom for i in reversed(y_coord)]

    #Consolidate coordinates
    x_coord_bottom = x_coord + x_inner_bottom
    y_coord_bottom = y_coord + y_inner_bottom

    ## MIDDLE AND UPPER QUADRILATERAL COORDINATES
    #Define z height
    middle_height = height + (collar_height * collar_ratio)
    top_height = height + collar_height
    z_coord_middle = [middle_height] * 4
    z_coord_top = [top_height] * 4

    #Define the inner points of the upper quadrilaterals of the collar
    distance_ratio_upper = (radius - collar_offset) / radius
    x_inner_upper = [i * distance_ratio_upper for i in reversed(x_coord)]
    y_inner_upper = [i * distance_ratio_upper for i in reversed(y_coord)]

    #Consolidate coordinates
    x_coord_upper = x_coord + x_inner_upper
    y_coord_upper = y_coord + y_inner_upper

    #Draw quadrilaterals
    bottom_quad = gen_sketch(x_coord_bottom, y_coord_bottom, z_coord_bottom)
    middle_quad = gen_sketch(x_coord_upper, y_coord_upper, z_coord_middle)
    top_quad = gen_sketch(x_coord_upper, y_coord_upper, z_coord_top)

    #Loft quadrilaterials
    lower_loft = add_loft(lofts,[bottom_quad, middle_quad])
    lower_body = lower_loft.bodies.item(0)
    upper_loft = add_loft(lofts,[middle_quad, top_quad])
    upper_body = upper_loft.bodies.item(0)

    #Combine into one collar body
    tools = adsk.core.ObjectCollection.create()
    tools.add(upper_body)
    combined_collar = combine_bodies(lower_body, tools)
    combined_collar_body = combined_collar.bodies.item(0)
    body_list.append(combined_collar_body)

    #GENERATE HOLES IF NEEDED
    if gen_collar_holes:
        #Find the point in the middle of the collar
        x_coord_hole = sum(x_coord)/len(x_coord)
        y_coord_hole = sum(y_coord)/len(y_coord)
        z_coord_hole = (height + top_height)/2
        hole_radius = (top_height - middle_height)/2

        #Find circle plane
        hole_plane_sketch = gen_sketch(x_coord * 2, y_coord * 2, [height, height] + [height + collar_height] * 2)
        hole_plane = construct_offset_plane(hole_plane_sketch, 0)

        # #Sketch circle
        hole_sketch = sketchObjs.add(hole_plane)
        hole_sketch_circle = hole_sketch.sketchCurves.sketchCircles
        hole_coordinates = hole_sketch.modelToSketchSpace(adsk.core.Point3D.create(x_coord_hole, y_coord_hole, z_coord_hole))
        cut_hole = hole_sketch_circle.addByCenterRadius(hole_coordinates, hole_radius)

        #Extrude circle
        cut_input = extrudeFeats.createInput(hole_sketch.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_distance = adsk.core.ValueInput.createByReal(radius*2)
        cut_input.setSymmetricExtent(cut_distance, True)
        cut_input.participantBodies = body_list
        ext = extrudeFeats.add(cut_input)

    return combined_collar_body

def createTubing(height, number_polygon_edges, top_rotation_angle, thickness, tube_OD):
    #Add holes for tubing
    #create offset plane from XY that's equal to the height of the Kresling
    top_plane = construct_offset_plane(rootComp.xYConstructionPlane, height)
    #sketch circles
    cut_circle_sketch = sketchObjs.add(top_plane)
    extrude_circle_sketch = sketchObjs.add(top_plane)
    cut_circles = cut_circle_sketch.sketchCurves.sketchCircles
    extrude_circles = extrude_circle_sketch.sketchCurves.sketchCircles
    #center circle
    cut_circles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), tube_OD/2)
    extrude_circles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), tube_OD/2 + thickness)
    #outside circles
    circleAngle = 2*math.pi/number_polygon_edges - top_rotation_angle
    for circle_count in range(3):
        #circle cutouts
        circleX = 2*radius/3 * math.cos(circleAngle + circle_count*2*math.pi/3)
        circleY = 2*radius/3 * math.sin(circleAngle + circle_count*2*math.pi/3)
        cut_circles.addByCenterRadius(adsk.core.Point3D.create(circleX,circleY,0), tube_OD/2)
        #circle lips
        extrude_circles.addByCenterRadius(adsk.core.Point3D.create(circleX,circleY,0), tube_OD/2 + thickness)

    circle_bodies = adsk.core.ObjectCollection.create()

    #Extrude lips for tubing
    for circle_count in range(4):
        ext_input = extrudeFeats.createInput(extrude_circle_sketch.profiles.item(circle_count), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(thickness*2)
        ext_input.setDistanceExtent(False, distance)
        ext = extrudeFeats.add(ext_input)
        ext_body = ext.bodies.item(0)
        circle_bodies.add(ext_body)

    #Cut circles for tubing
    for circle_count in range(4):
        cut_input = extrudeFeats.createInput(cut_circle_sketch.profiles.item(circle_count), adsk.fusion.FeatureOperations.CutFeatureOperation)
        distance = adsk.core.ValueInput.createByReal(thickness*2)
        cut_input.setDistanceExtent(False, distance)
        ext = extrudeFeats.add(cut_input)
    
    return circle_bodies

def make_chambers(lofts, outer_radius, inner_radius, chamber_thickness, draw_pts_x, draw_pts_y, draw_pts_z):
    chamber_bodies = []

    draw_pts_x = draw_pts_x[0:2]
    draw_pts_y = draw_pts_y[0:2]

    lower_chamber = make_chamber_walls(lofts, outer_radius, inner_radius, chamber_thickness, draw_pts_x, draw_pts_y, draw_pts_z[0:3], chamber_bodies)
    draw_pts_x.reverse()
    draw_pts_y.reverse()
    upper_chamber = make_chamber_walls(lofts, outer_radius, inner_radius, chamber_thickness, draw_pts_x, draw_pts_y, draw_pts_z[1:4], chamber_bodies)

    return chamber_bodies

def make_chamber_walls(lofts, outer_radius, inner_radius, chamber_thickness, draw_x, draw_y, draw_z, body_list):
    if draw_z[1] > draw_z[0]: #if the bottom triangle is being drawn
        second_radius = inner_radius
    else:
        second_radius = outer_radius

    points_x = make_chamber_points(outer_radius, second_radius, inner_radius - wall_thickness, draw_x)
    points_y = make_chamber_points(outer_radius, second_radius, inner_radius - wall_thickness, draw_y)

    chamber_triangle = param_Kresling(1, points_x, points_y, draw_z)
    chamber_parent = chamber_triangle.parentSketch

    front_chamber = create_hinge_extrude(chamber_parent, 0, chamber_thickness, 0)
    back_chamber = create_hinge_extrude(chamber_parent, 0, chamber_thickness, 1)
    body_list.append(front_chamber)
    body_list.append(back_chamber)

    return body_list 

def make_chamber_points(outer_radius, second_radius, inner_radius, draw_pts):
    #Take in chamber parameters and output the points to either side of the corner to loft between
    points_for_chamber = \
        [outer_radius * draw_pts[0], \
        second_radius * draw_pts[1], \
        inner_radius * draw_pts[0]]

    return points_for_chamber 

def param_Kresling(radius, points_x, points_y, points_z):
    #Multiply all points by radius
    points_x_parameterized = [i * radius for i in points_x]
    points_y_parameterized = [i * radius for i in points_y]

    #Make the Kresling triangle drawing
    Kresling_profile = gen_sketch(points_x_parameterized, points_y_parameterized, points_z)
    return Kresling_profile

def cut_combine(target_body, tool_body, keep_body):
    #Cut the tool body out of the target body
    tools = adsk.core.ObjectCollection.create()
    tools.add(tool_body)
    combine_input: adsk.fusion.CombineFeatureInput = combineFeats.createInput(target_body, tools)
    #Keep or discard tool body
    combine_input.isKeepToolBodies = keep_body
    combine_input.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    return combineFeats.add(combine_input)

def combine_bodies(target_body, tool_body_list):
    #target_body is a single body, tool_body_list is an Object Collection
    combine_input = combineFeats.createInput(target_body, tool_body_list)
    combine_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    combined_bodies_feat = combineFeats.add(combine_input)
    return combined_bodies_feat

def mirror_bodies(mirror_plane, mirror_bodies):
    #tool_body_list is an Object Collection
    mirror_input = mirrorFeats.createInput(mirror_bodies, mirror_plane)
    mirrored_body = mirrorFeats.add(mirror_input)
    return mirrored_body


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

    #Define offset direction by picking a point in the center of the geometry (centroid)
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

    #Offset sketch inwards (smaller than original sketch) by specified distance
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
    if offset_from_original != 0:
        offset_sketch_inside(hinge_sketch, offset_from_original)

    #Loft the original triangle to the hinge triangle
    hinge_profile = hinge_sketch.profiles.item(0)
    hinge_loft = add_loft(loftFeats,[original_profile, hinge_profile])

    return hinge_loft

def circular_pattern(input_bodies, pattern_num): 
    #Pattern around the y-axis
    z_axis = rootComp.zConstructionAxis
    
    #Define input
    circle_pattern_input = circlePatternFeats.createInput(input_bodies, z_axis)
    
    # Create patternNum of copies
    circle_pattern_input.quantity = adsk.core.ValueInput.createByReal(pattern_num)
    
    # Pattern symmetrically across 360 degrees
    circle_pattern_input.totalAngle = adsk.core.ValueInput.createByString('360 deg')
    circle_pattern_input.isSymmetric = True
    
    # Create the circular pattern
    circle_pat_feat = circlePatternFeats.add(circle_pattern_input)

    return circle_pat_feat

def rotate_around_z(input_bodies, input_angle):
    #input_bodies is an Object Collection of bodies
    move_input = moveFeats.createInput2(input_bodies)
    #Rotate around z-axis by top rotation angle
    real_angle = adsk.core.ValueInput.createByReal(input_angle)
    move_input.defineAsRotate(rootComp.zConstructionAxis, real_angle)
    return moveFeats.add(move_input)

def make_Kresling_body(lofts, radius, wall_thickness, hinge_thickness, number_polygon_edges, height, top_rotation_angle, base_thickness, lip_thickness, collar_height):
    #Create each Kresling triangle according to specified dimensions

    body_list = [] #Make an empty body list to append new bodies to

    #Create point lists for Kresling triangle points
    tri_points_x = generate_polygon_points(number_polygon_edges, top_rotation_angle, 0)
    tri_points_y = generate_polygon_points(number_polygon_edges, top_rotation_angle, math.pi/2)
    tri_points_z = [0, height, 0, height]

    #Draw upper and lower Kresling triangles from point lists
    circular_pattern_bodies = adsk.core.ObjectCollection.create() #create collection to pattern
    
    for lower_count in range(2):    
        #draw Kresling polygons for bottom of module, then top of module
        draw_points_x = tri_points_x[lower_count : lower_count + 3]
        draw_points_y = tri_points_y[lower_count : lower_count + 3]
        draw_points_z = tri_points_z[lower_count : lower_count + 3]

        outer_kresling = param_Kresling(radius - hinge_thickness, draw_points_x, draw_points_y, draw_points_z)
        inner_kresling = param_Kresling(radius - wall_thickness, draw_points_x, draw_points_y, draw_points_z)
        hinge_kresling_sketch = outer_kresling.parentSketch
        hinge_loft = create_hinge_extrude(hinge_kresling_sketch, hinge_offset, hinge_thickness, lower_count)

        #Add hinge bodies to list
        hinge_bodies = hinge_loft.bodies.item(0)
        body_list.append(hinge_bodies)
        circular_pattern_bodies.add(hinge_bodies)
        
        if hinge_thickness < wall_thickness:
            #Loft between interior and exterior Kresling faces, create bodies from loft features
            outer_loft = add_loft(lofts,[outer_kresling, inner_kresling]) 
            outer_bodies = outer_loft.bodies.item(0)
            body_list.append(outer_bodies)
            circular_pattern_bodies.add(outer_bodies)
        
        if chamber_length > 0:
            outer_center_kresling = param_Kresling((radius - chamber_length), draw_points_x, draw_points_y, draw_points_z)
            inner_center_kresling = param_Kresling((radius - chamber_length) - hinge_thickness, draw_points_x, draw_points_y, draw_points_z)

            #Generate center Kresling walls
            center_loft = add_loft(lofts,[inner_center_kresling, outer_center_kresling])
            center_bodies = center_loft.bodies.item(0)
            body_list.append(center_bodies)
            circular_pattern_bodies.add(center_bodies)
        
        #### Base, lip, and collar body generation

        base_points_x = tri_points_x[0::2]
        base_points_y = tri_points_y[0::2]
        base_points_x.append(0)
        base_points_y.append(0)
        
        if lower_count == 0 and base_thickness > 0 and gen_symmetric_collars == False:
            base_points_x = tri_points_x[0::2]
            base_points_y = tri_points_y[0::2]
            base_points_x.append(0)
            base_points_y.append(0)
            base_body = make_base(base_points_x, base_points_y, radius, 0, -1 * wall_thickness, lofts, body_list)
            circular_pattern_bodies.add(base_body)
        
        if collar_height <= 0:
            #Generate lid at the Kresling height if there is no collar
            lid_height = height
        elif lower_count == 0:
            #Make collar if collar height > 0
            collar_points_x = tri_points_x[1::2]
            collar_points_y = tri_points_y[1::2]
            collar_body = make_collar(collar_points_x, collar_points_y, radius, height, wall_thickness, collar_height, collar_ratio, collar_offset, gen_collar_holes, lofts, body_list)
            circular_pattern_bodies.add(collar_body)

            #Make mirrored collar
            if lower_count == 0 and gen_symmetric_collars:
                #Mirror plane
                collar_mirror_plane = construct_offset_plane(rootComp.xYConstructionPlane, height/2)
                #Mirror collar body
                collar_mirror_bodies = adsk.core.ObjectCollection.create()
                collar_mirror_bodies.add(collar_body)
                #Rotate mirrored collar body by top rotation angle
                mirrored_collar_body = mirror_bodies(collar_mirror_plane, collar_mirror_bodies).bodies.item(0)
                rotate_collar_bodies = adsk.core.ObjectCollection.create()
                rotate_collar_bodies.add(mirrored_collar_body)
                rotated_collar = rotate_around_z(rotate_collar_bodies, top_rotation_angle)
                #Circular pattern the collar body
                circular_pattern_bodies.add(mirrored_collar_body)
            
            #Generate lid above the collar
            lid_height = height + collar_height

        if lower_count == 1 and lip_thickness > 0:
            base_points_x = tri_points_x[1::2]
            base_points_y = tri_points_y[1::2]
            base_points_x.append(0)
            base_points_y.append(0)
            target_lip = make_base(base_points_x, base_points_y, radius, lid_height, wall_thickness, lofts, body_list)
            tool_lip = make_base(base_points_x, base_points_y, radius - wall_thickness, lid_height, wall_thickness, lofts, body_list)

            #Cut top out of the Kresling to make a lip
            cut_combine(target_lip, tool_lip, keepLid)
            circular_pattern_bodies.add(target_lip)

            #Make mirrored lip for mirrored collar
            if gen_symmetric_collars:
                lip_mirror_bodies = adsk.core.ObjectCollection.create()
                lip_mirror_bodies.add(target_lip)
                mirrored_lip_body = mirror_bodies(collar_mirror_plane, lip_mirror_bodies).bodies.item(0)
                #Rotate mirrored lip by top rotation angle
                rotate_lip_bodies = adsk.core.ObjectCollection.create()
                rotate_lip_bodies.add(mirrored_lip_body)
                rotated_lip = rotate_around_z(rotate_lip_bodies, top_rotation_angle)
                #Circular pattern the lip body
                circular_pattern_bodies.add(mirrored_lip_body)

            #Make lid
            if keepLid:
                circular_pattern_lid = adsk.core.ObjectCollection.create() #create collection to pattern lid
                circular_pattern_lid.add(tool_lip)

                #Circular pattern lid and combine the pieces
                patterned_lid = circular_pattern(circular_pattern_lid, number_polygon_edges)
                patterned_lid_bodies = adsk.core.ObjectCollection.create()
                for item_count in range(patterned_lid.bodies.count - 1): #ignore the original patterned body
                    patterned_lid_bodies.add(patterned_lid.bodies.item(item_count))
                combined_lid = combine_bodies(tool_lip, patterned_lid_bodies)
                combined_lid_body = combined_lid.bodies.item(0)

                #Make mirrored lid for mirrored collar
                if gen_symmetric_collars:
                    lid_mirror_bodies = adsk.core.ObjectCollection.create()
                    lid_mirror_bodies.add(combined_lid_body)
                    mirrored_lid_body = mirror_bodies(collar_mirror_plane, lid_mirror_bodies).bodies.item(0)
                    #Rotate mirrored lid by top rotation angle
                    rotate_lid_bodies = adsk.core.ObjectCollection.create()
                    rotate_lid_bodies.add(mirrored_lid_body)
                    rotated_lid = rotate_around_z(rotate_lid_bodies, top_rotation_angle)

                #Cut tubing
                if tube_OD > 0:
                    tubing_bodies = createTubing(lid_height, number_polygon_edges, top_rotation_angle, wall_thickness, tube_OD)
                    #Combine all lid bodies into one
                    combined_tube_lid = combine_bodies(combined_lid.bodies.item(0), tubing_bodies)
                    body_list.append(combined_tube_lid.bodies.item(0))
                else:
                    body_list.append(combined_lid.bodies.item(0))
        
    #Circular pattern all bodies by the number of Kresling polygon edges
    patterned_kresling = circular_pattern(circular_pattern_bodies, number_polygon_edges)
    body_list.append(patterned_kresling)
    
    circular_chamber_bodies = adsk.core.ObjectCollection.create() #create collection to pattern
    chamber_bodies = make_chambers(lofts, radius - wall_thickness, radius - chamber_length, wall_thickness, tri_points_x, tri_points_y, tri_points_z)
    
    for chamberBody in chamber_bodies:
        circular_chamber_bodies.add(chamberBody.bodies.item(0))
    circular_chambers = circular_pattern(circular_chamber_bodies, 3)

    body_list.append(circular_chambers)
    
    return body_list

##### Main code #####

# Create Fusion document 
app = adsk.core.Application.get()
ui = app.userInterface
doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
design = app.activeProduct

# Set up import functions
importManager = app.importManager

# Create sketch, construction plane, loft objects, and combine objects
rootComp = design.rootComponent
sketchObjs = rootComp.sketches
cPlaneObjs = rootComp.constructionPlanes
loftFeats = rootComp.features.loftFeatures
combineFeats = rootComp.features.combineFeatures
circlePatternFeats = rootComp.features.circularPatternFeatures
extrudeFeats = rootComp.features.extrudeFeatures
mirrorFeats = rootComp.features.mirrorFeatures
moveFeats = rootComp.features.moveFeatures

# Make Kresling structure
Kresling = make_Kresling_body(loftFeats, radius, wall_thickness, hinge_thickness, number_polygon_edges, height, top_rotation_angle, base_thickness, lip_thickness, collar_height)
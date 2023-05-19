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
chamber_length = 1.5

#Electrode .DXF filepath
electrode_filepath = ''#'C:/Users/oz/Downloads/electrode_dxf_mm.dxf'

#The distance between the original Kresling triangle and the hinge Kresling triangle
hinge_offset = 0.075
#this needs to be recalculated

#generate hinges on the inside faces of the Kresling if true, otherwise generate on the outside
inside_hinges = False

#generate hinges on the center kresling if true (hinges are always generated on inside AND outside faces)
#center_hinges = True

#generate hinges on the chamber walls if true (hinges are always generated on inside AND outside faces)
chamber_hinges = False

ratio_hinge_to_wall = 0.75
ratio_base_to_wall = 0
ratio_lip_to_wall = 0

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

def make_chambers(lofts, outer_radius, inner_radius, chamber_thickness, draw_pts_x, draw_pts_y, draw_pts_z):
    chamber_bodies = []

    draw_pts_x = draw_pts_x[0:2]
    draw_pts_y = draw_pts_y[0:2]

    lower_chamber = make_chamber_walls(lofts, outer_radius, inner_radius, chamber_thickness, draw_pts_x, draw_pts_y, draw_pts_z[0:3], chamber_bodies)
    draw_pts_x.reverse()
    draw_pts_y.reverse()
    upper_chamber = make_chamber_walls(lofts, outer_radius, inner_radius, chamber_thickness, draw_pts_x, draw_pts_y, draw_pts_z[1:4], chamber_bodies)

    #chamber_bodies.append(lower_chamber)
    #chamber_bodies.append(upper_chamber)
    return chamber_bodies

def make_chamber_walls(lofts, outer_radius, inner_radius, chamber_thickness, draw_x, draw_y, draw_z, body_list):
    
    if draw_z[1] > draw_z[0]: #if the bottom triangle is being drawn
        second_radius = inner_radius
    else:
        second_radius = outer_radius

    points_x = make_chamber_points(outer_radius, second_radius, inner_radius, draw_x)
    points_y = make_chamber_points(outer_radius, second_radius, inner_radius, draw_y)

    chamber_triangle = param_Kresling(1, points_x, points_y, draw_z)
    chamber_parent = chamber_triangle.parentSketch

    front_chamber = create_hinge_extrude(chamber_parent, 0, chamber_thickness/2, 0)
    back_chamber = create_hinge_extrude(chamber_parent, 0, chamber_thickness/2, 1)

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

    #Note to Ash: Is flip value behavior right?
    #Create construction plane by offsetting the original profile by the hinge thickness
    if upper_or_lower == 0: #0 is lower
        hinge_plane_offset = hinge_loft_thickness
    else:
        hinge_plane_offset = hinge_loft_thickness * (-1) #if a hinge is being generated on an upper plane, the offset must be reversed
         
    hinge_plane = construct_offset_plane(original_profile, hinge_plane_offset)

    #Project the original sketch onto the construction plane in a new sketch
    hinge_sketch = project_sketch(original_sketch, hinge_plane)
    #Offset the projection on the new sketch by however much the hinge triangle is smaller than the original
    if offset_from_original > 0:
        offset_sketch_inside(hinge_sketch, offset_from_original)

    #Loft the original triangle to the hinge triangle
    hinge_profile = hinge_sketch.profiles.item(0)
    hinge_loft = add_loft(loftFeats,[original_profile, hinge_profile])

    return hinge_loft

def deboss_electrode(dxf_file_path, import_sketch):
    #Create construction plane to import on
    import_profile = import_sketch.profiles.item(0)
    import_plane = construct_offset_plane(import_profile, 0)
    #Set up import on import plane
    import_options = importManager.createDXF2DImportOptions(dxf_file_path, import_plane)
    importManager.importToTarget(import_options, rootComp)
    electrode_sketch = import_options.results.item(0)

    #Project important geometry for constraints
    kresling_point = electrode_sketch.project(import_sketch.sketchPoints.item(2))
    kresling_line = electrode_sketch.project(import_sketch.sketchCurves.sketchLines.item(0))

    #Constrain point
    constraints = electrode_sketch.geometricConstraints
    coincident_constraint = constraints.addCoincident(electrode_sketch.sketchPoints.item(17), electrode_sketch.sketchPoints.item(5))

    #The order of the DXF points keeps changing, this is not a reliable method
    # 7 points in sketch, 17 in dxf

    return

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

def make_Kresling_body(lofts, radius, wall_thickness, hinge_thickness, number_polygon_edges, height, top_rotation_angle, base_thickness, lip_thickness):
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
        
        '''
        #Recommend deleting this code because hinges cannot be on the inside of the module due to 3D printing constraints
        #Generate hinges on either the inside or the outside
        if inside_hinges:
            #Outer kresling is radius of Kresling when hinges are inside
            outer_kresling = param_Kresling(radius, draw_points_x, draw_points_y, draw_points_z)
            inner_kresling = param_Kresling(radius - wall_thickness + hinge_thickness, draw_points_x, draw_points_y, draw_points_z)
            hinge_kresling_sketch = inner_kresling.parentSketch
            
            #Flip the offset direction of the hinge plane generation based on upper or lower Kresling face
            if m == 0:
                flip_value = 1
            elif m == 1:
                flip_value = 0
            Does the fix below, multiplying by -1, solve it?
            
           
            hinge_loft = create_hinge_extrude(hinge_kresling_sketch, hinge_offset, hinge_thickness, -1 * lower_count)

        else:
            #Outer kresling is radius of Kresling MINUS hinge thickness when hinges are outside
            outer_kresling = param_Kresling(radius - hinge_thickness, draw_points_x, draw_points_y, draw_points_z)
            inner_kresling = param_Kresling(radius - wall_thickness, draw_points_x, draw_points_y, draw_points_z)
            hinge_kresling_sketch = outer_kresling.parentSketch
            hinge_loft = create_hinge_extrude(hinge_kresling_sketch, hinge_offset, hinge_thickness, lower_count)
        '''

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

        if electrode_filepath != '':
            #Add deboss for electrodes
            deboss_electrode(electrode_filepath, outer_kresling.parentSketch)
        
        if chamber_length > 0:
            outer_center_kresling = param_Kresling((radius - chamber_length), draw_points_x, draw_points_y, draw_points_z)
            inner_center_kresling = param_Kresling((radius - chamber_length) - hinge_thickness, draw_points_x, draw_points_y, draw_points_z)

            #Generate center Kresling walls
            center_loft = add_loft(lofts,[inner_center_kresling, outer_center_kresling])
            center_bodies = center_loft.bodies.item(0)
            body_list.append(center_bodies)
            circular_pattern_bodies.add(center_bodies)

            '''
            #Recommend deleting code below since the chambers will always be printed with thinnest possible walls, so no hinges
            #Generate hinged lofts on the inside and outside of the center Kresling
            if center_hinges:
                outer_center_kresling = param_Kresling((radius - chamber_length) - (hinge_thickness / 3), points_x, points_y, points_z)
                inner_center_kresling = param_Kresling((radius - chamber_length) - (hinge_thickness * 2 / 3), points_x, points_y, points_z)
                hinge_center_kresling_sketch = outer_center_kresling.parentSketch
                hinge_loft = create_hinge_extrude(hinge_center_kresling_sketch, hinge_offset, hinge_thickness/3, lower_count)
                #Add hinge bodies to list
                hinge_bodies = hinge_loft.bodies.item(0)
                body_list.append(hinge_bodies)
                circular_pattern_bodies.add(hinge_bodies)
                if lower_count == 0:
                    flip_value = 1
                elif lower_count == 1:
                    flip_value = 0
                hinge_center_kresling_sketch = inner_center_kresling.parentSketch
                hinge_loft = create_hinge_extrude(hinge_center_kresling_sketch, hinge_offset, hinge_thickness/3, flip_value)
                #Add hinge bodies to list
                hinge_bodies = hinge_loft.bodies.item(0)
                body_list.append(hinge_bodies)
                circular_pattern_bodies.add(hinge_bodies)
            #Generate non-hinged lofts for the center Kresling
            else:
                outer_center_kresling = param_Kresling((radius - chamber_length), points_x, points_y, points_z)
                inner_center_kresling = param_Kresling((radius - chamber_length) - hinge_thickness, points_x, points_y, points_z)
            '''
        
        #### Base and lip body generation

        base_points_x = tri_points_x[0::2]
        base_points_y = tri_points_y[0::2]
        base_points_x.append(0)
        base_points_y.append(0)
        
        if lower_count == 0 and base_thickness > 0:
            base_body = make_base(base_points_x, base_points_y, radius, 0, -1 * wall_thickness, lofts, body_list)
            circular_pattern_bodies.add(base_body)
        
        if lower_count == 1 and lip_thickness > 0:
            target_lip = make_base(base_points_x, base_points_y, radius, height, wall_thickness, lofts, body_list)
            tool_lip = make_base(base_points_x, base_points_y, radius - wall_thickness, height, wall_thickness, lofts, body_list)

            #Cut top out of the Kresling to make a lip
            cut_lip = cut_combine(target_lip, tool_lip)
            #circular_pattern_bodies.add(cut_lip)
            #Note to Ash: Adding the lip is failing for right now, returns a feature and not a body...unsure how to proceed.
        
    #Circular pattern all bodies by the number of Kresling polygon edges
    patterned_kresling = circular_pattern(circular_pattern_bodies, number_polygon_edges)
    body_list.append(patterned_kresling)
    
    '''
    #Again recommending deletion since hinges will always be on the outside
    if inside_hinges:
        chamber_outer_radius = radius
    else:
        chamber_outer_radius = radius - hinge_thickness

    if center_hinges:
        chamber_inner_radius = (radius - chamber_length) - hinge_thickness/3
    else:
        chamber_inner_radius = radius - chamber_length
    
    make_chambers(lofts, number_polygon_edges, chamber_outer_radius, chamber_inner_radius, top_rotation_angle, height, lower_x, lower_y, upper_x, upper_y)
    '''
    #Note to Ash: Circular pattern is not working with the chambers. Can you take a look?
    chamber_body_list = []
    circular_chamber_bodies = adsk.core.ObjectCollection.create()
    chamber_bodies = make_chambers(lofts, radius - wall_thickness, radius - chamber_length, wall_thickness, tri_points_x, tri_points_y, tri_points_z)
    chamber_body_list.append(chamber_bodies.bodies.item(0))
    circular_chamber_bodies.add(chamber_body_list)
    circular_pattern(circular_chamber_bodies, 3)
    body_list.append(patterned_kresling)

    

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

# Make Kresling structure
Kresling = make_Kresling_body(loftFeats, radius, wall_thickness, hinge_thickness, number_polygon_edges, height, top_rotation_angle, base_thickness, lip_thickness)

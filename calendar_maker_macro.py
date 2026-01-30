import FreeCAD as App
import FreeCADGui as Gui
import Part
import math

#App.newDocument("Test")

print("Running...")
# ==================================================
# DOCUMENT SETUP
# ==================================================
# FreeCAD has a document/model layer (geometry)
# and a GUI/view layer (colors, labels, visibility).
#
# We always start from a clean document so the
# macro is deterministic and easy to reason about.
# ==================================================

doc = App.ActiveDocument or App.newDocument("GridHoles")

# Remove all existing objects so each run starts clean
for obj in doc.Objects:
    doc.removeObject(obj.Name)
doc.recompute()

# ==================================================
# HOLE GRID PARAMETERS
# ==================================================
# IMPORTANT CHANGE:
# Openings are now RECTANGULAR, not square
# ==================================================

print("Letter Paper Width = 279.4")
print("Letter Paper Height = 215.9")

hole_width  = 35.5    # mm (X size of each opening)
hole_height = 35.5    # mm (Y size of each opening)
hole_radius = 2.8     # mm (corner fillet radius)

n_cols  = 7         # columns in X
n_rows  = 5         # rows in Y
spacing = 5         # gap between holes (both X and Y)

display_width = n_cols*hole_width+ (n_cols-1)*spacing
display_height = n_rows*hole_height+ (n_rows-1)*spacing
print(f"{display_width=}")
print(f"{display_height=}")





# ==================================================
# PLATE (BASE SOLID) PARAMETERS
# Coordinate system reminder:
#   X → left/right
#   Y → front/back
#   Z → up (thickness)
# ==================================================

plate_width  = n_cols*hole_width + (n_cols+1)*spacing #292   # mm (X)

# REAL PAGE CALENDAR
plate_height = 220 #n_rows*hole_height + (n_rows+1)*spacing + 20 #220       # mm (Y)
header_height = plate_height - (n_rows*hole_height + (n_rows+1)*spacing)

## TEST PRINT
#header_height is how much BIGGER the top is than a typical spacing row
#header_height = 12.5 # plate_height - (n_rows*hole_height + (n_rows+1)*spacing)
#plate_height = n_rows*hole_height + (n_rows+1)*spacing + header_height #220       # mm (Y)

print(f"{plate_height=}")
print(f"{plate_width=}")



print(f"{header_height=}")
front_thickness = 2.8 #mm thickness of the front (the side with the holes)
back_thickness = 3.2 #2.4 #mm thickness of the back (the side that is solid)
slot_thickness = 1.0 #mm thickness of the slot for the paper
thickness    = front_thickness + back_thickness + slot_thickness         # mm (Z)

# Aliases you were already using
width  = plate_width
length = plate_height


# ==================================================
# COMPUTE GRID SIZE AND CENTER IT ON THE PLATE
# ==================================================

grid_width  = n_cols * hole_width  + (n_cols - 1) * spacing
grid_height = n_rows * hole_height + (n_rows - 1) * spacing

x_start = (plate_width  - grid_width)  / 2
y_start = spacing
# (You intentionally offset upward instead of centering)

# ==================================================
# CREATE BASE PLATE (GEOMETRY ONLY)
# ==================================================
# Part.makeBox() creates a *shape* (pure geometry).
# Nothing appears in the 3D view until Part.show().
# ==================================================

base = Part.makeBox(
    plate_width,
    plate_height,
    thickness
)

    
# Helper function for filelts
def is_vertical_y_edge(edge, tol=1e-6):
    """
    Returns True if edge is vertical (Z changes)
    and aligned with Y (X constant).
    """
    v0, v1 = edge.Vertexes
    return (
        abs(v0.Z - v1.Z) > tol and
        abs(v0.X - v1.X) < tol
    )

# ==================================================
# COLLECT Y-DIRECTION EDGES FOR FILLETING
# ==================================================

#Make a "chamfillet" for the first layer where y==plate_height, and fillets elsewhere
#CHAMFER the bottom for better first layer

chamfillet_height = 0 #plate_height

outer_y_edges = []

for e in base.Edges:
    v0,v1 = e.Vertexes
    if abs(v0.Y - chamfillet_height)<1e-4 and is_vertical_y_edge(e): # and is_vertical_y_edge(e): 
        outer_y_edges.append(e)

outer_y_fillet_radius = 1.0 #hole_radius #3.0   # mm (outer plate edges)
if outer_y_edges:
    #base = base.makeFillet(outer_y_fillet_radius, outer_y_edges)
    base = base.makeChamfer(outer_y_fillet_radius, outer_y_edges)

### FILLET for things off of the top now
outer_y_edges = []
       
for e in base.Edges:
    v0,v1 = e.Vertexes
    if abs(v0.Y - chamfillet_height) > 1e-5 and is_vertical_y_edge(e): # and (is_vertical_y_edge(e) or abs(v0.Y - chamfillet_height)<outer_y_fillet_radius + 1e-4):
        outer_y_edges.append(e)
            #if abs(v0.Y - plate_height) > 1e-5 : #or is_vertical_y_edge(e):
        #	outer_y_edges.append(e)

outer_y_fillet_radius = hole_radius #3.0   # mm (outer plate edges)
if outer_y_edges:
    base = base.makeFillet(outer_y_fillet_radius, outer_y_edges)
    #base = base.makeChamfer(outer_y_fillet_radius, outer_y_edges)
    
    
       
                
                                
##################
# Chamfer evertyhign a tiny bit
#####################

#tiny_chamfer_radius = 1.0 #0.8
#base = base.makeChamfer(tiny_chamfer_radius, base.Edges)


# ==================================================
# HELPER: CREATE A ROUNDED RECTANGULAR CUTTER
# ==================================================
# This returns a SOLID that will be subtracted
# from the base using boolean operations.
# ==================================================

def rounded_rectangle(x, y, z, w, h, radius, height):
    """
    Create a rectangular prism with vertical edges filleted,
    then move it into position.
    """

    # Create rectangular prism
    rect = Part.makeBox(w, h, height)

    # Collect ONLY vertical edges (parallel to Z)
    vertical_edges = []
    for e in rect.Edges:
        v0, v1 = e.Vertexes
        if abs(v0.Z - v1.Z) > 1e-6:
            vertical_edges.append(e)

    # Apply fillet to vertical edges
    rect = rect.makeFillet(radius, vertical_edges)
    
    #rect = rect.makeChamfer(radius, vertical_edges)

    # Move into final position
    # NOTE: THe final position is at thickness-height into the part!
    
    rect.translate(App.Vector(x, y, z ))
    return rect

# ==================================================
# CREATE ALL HOLE CUTTERS
# ==================================================

holes = []

for row in range(n_rows):
    for col in range(n_cols):
        x = x_start + col * (hole_width + spacing)
        y = y_start + row * (hole_height + spacing)
        holes.append(
            rounded_rectangle(
                x,
                y,
                back_thickness+slot_thickness,
                hole_width,
                hole_height,
                hole_radius,
                front_thickness
            )
        )
   

# ==================================================
# SUBTRACT HOLES FROM BASE
# ==================================================
# IMPORTANT CONCEPT:
# base.cut(hole) does NOT modify base.
# It returns a NEW shape.
# ==================================================

for h in holes:
    base = base.cut(h)
  
###############      
#fillet only edges on the outer plane now
#################

#face_edges = []
#for e in base.Edges:
#    v0, v1 = e.Vertexes
#    if (abs(v0.Z - thickness) < 0.001 and abs(v1.Z - thickness)<0.001) or (abs(v0.Z - 0.0) < 0.001 and abs(v1.Z - 0.0)<0.001) :
#        face_edges.append(e)

#tiny_chamfer_radius = 0.4
#if face_edges:
   #base = base.makeChamfer(tiny_chamfer_radius, face_edges)
#   base = base.makeFillet(tiny_chamfer_radius, face_edges)
   
    
# ==================================================
# CREATE CENTRAL SLOT CUTTER
# ==================================================
# This is a thin internal void down the middle
# ==================================================

slot_fillet_radius = 0.4   # mm (outer plate edges)
slot_plunge = 2.4 # mm how far to plunge down into the bottom edge
slot_side = 1.35 #mm how far to cut into the sides
# ALREADY DEINFED THIS slot_thickness = 1.0  # mm (Z direction)

slot_width  = n_cols*hole_width + (n_cols-1)*spacing + 2*slot_fillet_radius + 2*slot_side #plate_width  - 2 * spacing
print(f"{slot_width=}")

slot_height = plate_height - spacing + 2*slot_fillet_radius + slot_plunge # mm (outer plate edges)
print(f"{slot_height=}") 

# Slot position
slot_x = spacing - slot_side - slot_fillet_radius 
slot_y = spacing - slot_plunge - slot_fillet_radius
slot_z = back_thickness #+ (slot_thickness / 2)  # center in Z

# Create slot solid
slot = Part.makeBox(
    slot_width,
    slot_height,
    slot_thickness
)

#
#### 


# Move slot into place
slot.translate(App.Vector(slot_x, slot_y, slot_z))

def is_vertical_z_edge(edge, tol=1e-6):
    """
    Returns True if the edge is vertical (parallel to Z axis),
    meaning X and Y are constant and Z changes.
    """
    v0, v1 = edge.Vertexes
    return (
        abs(v0.Z - v1.Z) > tol and
        abs(v0.X - v1.X) < tol and
        abs(v0.Y - v1.Y) < tol
    )
    
slot_z_edges = []

for e in slot.Edges:
    #if is_vertical_z_edge(e):
    slot_z_edges.append(e)


if slot_z_edges:
    slot = slot.makeFillet(slot_fillet_radius, slot_z_edges)
    
   



# Subtract slot from base
base = base.cut(slot)

###########################
############ FILLET EDGES
############################

# Helper function for filelts
def is_horiz_x_edge(edge, tol=1e-6):
    """
    Returns True if edge is X horiz (X changes) only
    """
    v0, v1 = edge.Vertexes
    return (
        
        abs(v0.X - v1.X) > tol 
    )
    
def is_y_edge(edge, toll=1e-6):
    """
    Returns True if edge is X horiz (X changes) only
    """
    v0, v1 = edge.Vertexes
    return (
        abs(v0.Y - v1.Y) > toll and
        abs(v0.X - v1.X) < toll and
        abs(v0.Z - v1.Z) < toll 
        
    )    



allowed_z_values = [0.0,thickness, back_thickness + slot_thickness ]
tol = 1e-6
face_edges = []
for e in base.Edges:
    if len(e.Vertexes) == 2:
        v0, v1 = e.Vertexes
        for my_z in allowed_z_values:
            #print(is_horiz_x_edge(e))hole_height - tol
            if abs(v0.Y - v1.Y) > 1.0  and (abs(v0.Z - my_z) < tol and abs(v1.Z - my_z)<tol) and (abs(v0.Y) > tol and abs(v1.Y)>tol):
                #we also dont want to touch any edges on the buildplate
                face_edges.append(e)
                continue

tiny_chamfer_radius = 1.2
if face_edges:
   #pass
   #base = base.makeChamfer(tiny_chamfer_radius, face_edges)
   base = base.makeFillet(tiny_chamfer_radius, face_edges)
   #pass
   # ==================================================
# ADD VERTICAL RELIEF CUTOUTS (STAGGERED)
# ==================================================
print("Adding vertical relief cutouts...")

relief_radius = 0.8
relief_off_top = 0.4
relief_off_bottom = 2
# We make the cylinder slightly longer than the plate to ensure a clean cut
relief_height = plate_height - (relief_off_top + relief_off_bottom) 
def make_relief_cutout(x_pos, z_pos, my_end_z=0):
    # Create the cylinder
    relief = Part.makeCylinder(relief_radius, relief_height - my_end_z)
    
    # Rotate to run vertically along Y axis (front-to-back)
    relief.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
    
    # Position it
    # X: At the calculated staggered position
    # Y: Centered or starting at bottom (we'll start at -5 to over-cut)
    # Z: At the specified depth (front face or back face)
    relief.translate(App.Vector(x_pos, plate_height - relief_off_bottom - my_end_z, z_pos))
    return relief

relief_cutters = []

for i in range(1, n_cols):
    # 1. Front-side cutouts (behind the posts, invisible from front)
    # Positioning logic: exactly at the center of the vertical posts
   
    x_front = x_start + i * (hole_width + spacing) - (spacing / 2.0)
    # Z position: flush with the front face (thickness)
    z_front = front_thickness + 0.5*slot_thickness
    relief_cutters.append(make_relief_cutout(x_front, z_front))

n_cutouts_per_col = 3
for i in range(n_cols*n_cutouts_per_col):
    # 2. Back-side cutouts (staggered - in the middle of the holes)
    # Positioning logic: center of the hole openings
    x_back = x_start + (i + 0.5 )* (hole_width + spacing)/(n_cutouts_per_col) - (spacing/2)
    # Z position: flush with the back face (0)
    z_back = 0
    if i in [0,1,n_cols*n_cutouts_per_col-2,n_cols*n_cutouts_per_col-1]:
        my_end_z = 70
        #make the last few a bit shorter to leave room for command strips
    else:
        my_end_z = 0
   
    relief_cutters.append(make_relief_cutout(x_back, z_back,my_end_z))

# Subtract all relief cutouts from the base
for cutter in relief_cutters:
    base = base.cut(cutter)
    
# ==================================================
# ENGRAVE WEEKDAY LETTERS ON CALENDAR PLATE
# ==================================================
import Draft

# Days of the week
day_labels = ["Su","Mo","Tu","We","Th","Fr","Sa"] #["♥","♥"] #["♥","Ezra"] 
labels_to_use = day_labels[:n_cols]  # match number of columns

# Compute top free area above holes
grid_height = n_rows * hole_height + (n_rows - 1) * spacing
grid_top_y = y_start + grid_height
top_free_height = plate_height - grid_top_y

# Text parameters
font_file = "Users/mnica/Downloads/Zoia-Stencil-Mihai4.ttf" #"/Library/Fonts/zoia-stencil.ttf" #"/System/Library/Fonts/Supplemental/Arial.ttf" #"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # update to a font on your system
text_height = top_free_height * 0.7  # approximate height in mm
engrave_depth = front_thickness #0.8                  # depth of engraving
text_z = thickness #- engrave_depth   # start just below top surface

text_shapes = []

# --- Create a list to store temporary text objects ---
temp_text_objects = []

for col, label in enumerate(labels_to_use):
    # X center of this column
    col_x_center = x_start + col * (hole_width + spacing) + hole_width/2
    # Y position in middle of top free area
    text_y_center = grid_top_y + top_free_height / 2

    # Create ShapeString (correct syntax)
    ss = Draft.make_shapestring(String=label, FontFile=font_file, Size=text_height)
    #doc.removeObject(ss.Name)  # remove Draft object; we just need the geometry
    ss.ViewObject.Visibility = False
    temp_text_objects.append(ss)

    # Get bounding box to center the shape
    bb = ss.Shape.BoundBox
    shape_copy = ss.Shape.copy()
    shape_copy.translate(App.Vector(
        col_x_center - (bb.XMin + bb.XMax)/2,
        text_y_center - (bb.YMin + bb.YMax)/2,
        text_z
    ))

    # Extrude downward to cut engraving
    engraved_solid = shape_copy.extrude(App.Vector(0,0,-engrave_depth))
    text_shapes.append(engraved_solid)
    #my_part = Part.show(engraved_solid)
    #my_part.Label = label

# Cut all letters from base
for txt in text_shapes:
    base = base.cut(txt)
    
for obj in temp_text_objects:
    ss.ViewObject.Visibility = False
    
   


# Make the base vertical and rotate diagonally
# 1. Rotate 90° around X to stand it up in Z
rot_x = App.Rotation(App.Vector(1,0,0), 90)
# 2. Rotate 45° around Z to put it diagonally
rot_z = App.Rotation(App.Vector(0,0,1), 0) #45)
# Combine rotations: X first, then Z
rot_y = App.Rotation(App.Vector(0,1,0), 0) # 180)
# Combine rotations: X first, then Z

combined_rot = rot_y.multiply(rot_z.multiply(rot_x))

# Apply rotation, keeping the base at the same origin
base.Placement = App.Placement(base.Placement.Base, combined_rot)


all_parts = []

# ==================================================
# ADD TWO CIRCULAR MOUSE EARS (CORNERS ONLY)
# ==================================================
print("Creating circular anchor ears at corners...")

ear_radius = 15.0    # Size of the circle
ear_height = 0.2     # 1 layers thick
# We center the circles on the Y-axis of the standing calendar
ear_y = -thickness / 2.0 
ear_x = 10

# Perforation settings
slot_width = 0.9      # Width of the air gap (X direction)
slot_depth = 15.0     # How far to cut into the ear (Y direction)
# thickness is the calendar's width on the build plate

def make_square_ear(x_pos, rotated=False):
    # 1. Create a Square (Box)
    side = ear_radius * 2
    ear = Part.makeBox(side, side, ear_height)
    
    # 2. Fillet the 4 vertical corners
    # These are the edges where Z goes from 0 to ear_height
    fillet_edges = []
    for e in ear.Edges:
        v0, v1 = e.Vertexes
        # If it's a vertical edge (X and Y don't change, but Z does)
        if abs(v0.X - v1.X) < 1e-6 and abs(v0.Y - v1.Y) < 1e-6:
            fillet_edges.append(e)
    
    if fillet_edges:
        # A fillet radius of ear_radius would make it a circle again.
        # We use a smaller value (e.g., 25% of the side) to keep the diamond look.
        f_rad = side * 0.25 
        ear = ear.makeFillet(f_rad, fillet_edges)

    # 3. Center the square so (0,0) is the middle
    ear.translate(App.Vector(-side/2.0, -side/2.0, 0))
    
    # 4. Rotate 45 degrees to make it a Diamond
    ear.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 45)
    
    # 5. Optional 180-degree flip
    if rotated:
        ear.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180)
    
    # 6. Final positioning
    ear.translate(App.Vector(x_pos, ear_y, 0))
    
    return ear

def make_snap_ear2(x_pos,rotated=False):
    # 1. Create the base disk
    ear = Part.makeCylinder(ear_radius, ear_height)
    
    # 2. Create cutters to run along the thickness edges
    # These will be thin boxes placed at the front and back edges of the plate
    cutter_front = Part.makeBox(ear_radius*0.25, slot_width, ear_height + 1)
    cutter_back  = Part.makeBox(ear_radius*0.25, slot_width, ear_height + 1)
    
    # 3. Position the cutters
    # We want them at Y = 0 and Y = thickness
    # Note: the ear itself is currently at (0,0) in its local space
    # The ear will be translated to ear_y (thickness/2) later.
   
    
    
    # Shift cutters so they align with the plate edges in local space
    # (Since the ear will be centered at thickness/2, the edges are at +/- thickness/2)
    cutter_front.translate(App.Vector(-ear_radius, thickness/2.0, -0.5))
    cutter_back.translate(App.Vector(-ear_radius, -thickness/2.0-slot_width, -0.5))
    
    # 4. Subtract the cutters from the ear
    #ear_with_slots = ear.cut(cutter_front).cut(cutter_back)
    #if rotated:
    #   # 5. NEW: Rotate the ear 180 degrees around the Z-axis
    #    # Arguments: (Center Point, Axis Vector, Angle)
    #    ear_with_slots.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180)
    
    
    
    # 5. Final positioning to the calendar corner
    ear_with_slots = ear
    ear_with_slots.translate(App.Vector(x_pos, ear_y, 0))
    
    return ear_with_slots

# Create the two ears
left_ear = make_square_ear(ear_x,True)
right_ear = make_square_ear(plate_width-ear_x,False)

# Show them (optional, for visual check)
obj_e1 = Part.show(left_ear, "MouseEar_L")
obj_e2 = Part.show(right_ear, "MouseEar_R")

#move the base up/down to cut out slots in the mouse ears
slot_width = 0.4

base.translate(App.Vector(0,slot_width,0))
left_ear = left_ear.cut(base)
right_ear = right_ear.cut(base)

base.translate(App.Vector(0,-2*slot_width,0))
left_ear = left_ear.cut(base)
right_ear = right_ear.cut(base)

base.translate(App.Vector(0,slot_width,0))



#base = base.cut(left_ear).cut(right_ear)


#one last mini chamfer on the bottom x edge

# Helper function for filelts
def is_vertical_x_edge(edge, tol=1e-6):
    """
    Returns True if edge is vertical (Z changes)
    and aligned with Y (X constant).
    """
    v0, v1 = edge.Vertexes
    return (
        abs(v0.Z - v1.Z) < tol and
        abs(v0.Y - v1.Y) < tol and
        abs(v0.X - v1.X) > tol
    )
#cham_height = ear_height
#outer_x_edges = []
       
#for e in base.Edges:
#    if len(e.Vertexes) == 2:
#        v0,v1 = e.Vertexes
##        if abs(v0.Z - cham_height) < 1e-5 and is_vertical_x_edge(e): # and (is_vertical_y_edge(e) or abs(v0.Y - chamfillet_height)<outer_y_fillet_radius + 1e-4):
#            outer_x_edges.append(e)
            #if abs(v0.Y - plate_height) > 1e-5 : #or is_vertical_y_edge(e):
        #	outer_y_edges.append(e)

#outer_x_cham_radius = 0.6 #3.0   # mm (outer plate edges)
#if outer_y_edges:
#    #base = base.makeFillet(outer_y_fillet_radius, outer_y_edges)
#    base = base.makeChamfer(outer_x_cham_radius, outer_x_edges)



# Show final plate
obj_base = Part.show(base)
obj_base.Label = "Calendar"
doc.recompute()

# Add shapes to the master fusion list
all_parts = [obj_base.Shape, left_ear, right_ear]

doc.recompute()
print(f"Anchors placed at X=0 and X={plate_width}")

# ==================================================
# ADD SUPPORT FINS
# ==================================================
print("Adding support fins...")

    
def make_fin(width_base, width_top, height, thick, fillet_val, 
             strut_radius=0.6, strut_spacing=15.0, strut_offset_z=3.0, strut_len=3.0):
    
    # 1. Create the Trapezoid profile (as before)
    pts = [
        App.Vector(0, 0, 0),               
        App.Vector(0, width_base, 0),            
        App.Vector(0, width_top, height), 
        App.Vector(0, 0, height),      
        App.Vector(0, 0, 0)                
    ]
    wire = Part.makePolygon(pts)
    face = Part.Face(wire)
    fin = face.extrude(App.Vector(thick, 0, 0))
    
     # 4. Apply Fillet
    fillet_edges = []
    for e in fin.Edges:
        if len(e.Vertexes) == 2:
            v0, v1 = e.Vertexes
        # Rule 1: Exclude edges parallel to the ground (Z doesn't change)
            is_parallel_to_ground = abs(v0.Z - v1.Z) < 1e-6
        # Avoid the bottom (Z=0)
            is_on_ground = abs(v0.Z) < 1e-6 and abs(v1.Z) < 1e-6
        # Avoid the back wall (Y=0) where the chamfer is
            is_on_back_wall = abs(v0.Y) < 1e-2 and abs(v1.Y) < 1e-2
        
        # We want to fillet:
        # - The top horizontal edge
        # - The diagonal slope
        # - The front vertical edge (if it exists)
            if not is_parallel_to_ground and not is_on_ground : #and not is_on_back_wall:
                fillet_edges.append(e)
            
    if fillet_edges:
        try:
            fin = fin.makeFillet(fillet_val, fillet_edges)
        except:
            print("Fillet still struggling, skipping to keep macro running.")
            
    # --- NEW: HOLLOWING (OPEN TOP) LOGIC ---
    shell_thickness = 0.8  # Thickness of the walls
    
    # Find the top face (the one with the highest Z coordinate)
    faces_to_remove = []
    max_z = -1.0
    top_face = None

    for f in fin.Faces:
        if f.CenterOfMass.z > max_z:
            max_z = f.CenterOfMass.z
            top_face = f
    
    if top_face:
        faces_to_remove.append(top_face)
    
    if faces_to_remove:
        try:
            # Negative thickness shells "inward"
            fin = fin.makeThickness(faces_to_remove, -shell_thickness, 1e-3)
            print("Fin successfully hollowed (top open).")
        except:
            print("Hollowing failed, keeping solid.")
    # ---------------------------------------
        
    
    # 2. Add Horizontal Support Cylinders (The "Comb")
    # We'll place these on the face of the fin (at X=thick)
    struts = []
    current_z = strut_offset_z
    
    # Calculate how long the strut needs to be to reach the calendar.
    # We assume the fin Y=0 is the calendar face.
    # The struts run in the -Y direction.
    
    
    strut_taper_radius = 0.3
    while current_z < height: # Stop 5mm from the top
        # Create cylinder: (radius, height)
        # Note: Cylinder is created along Z by default, we need to rotate it
        #strut = Part.makeCylinder(strut_radius, strut_len)# Part.makeCone(radius1, radius2, height)
        # radius1 is the base (at the fin), radius2 is the tip (at the calendar)
        strut = Part.makeCone(strut_radius, strut_taper_radius, strut_len)
        
        # Rotate 90 deg around X so it points along Y axis
        strut.rotate(App.Vector(0,0,0), App.Vector(1,0,0), 90)
        
        # Position it: 
        # X: centered on the fin thickness
        # Y: starting at the fin face (0) and going toward calendar
        # Z: current height
        strut.translate(App.Vector(thick/2.0, 0, current_z))
        
        struts.append(strut)
        current_z += strut_spacing

    # 3. Fuse the struts to the fin
    if struts:
        fin = fin.multiFuse(struts)
        
    # 4. Fillet the Strut Connections
    connection_fillets = []
    for e in fin.Edges:
        if hasattr(e, "Curve") and isinstance(e.Curve, Part.Circle):
            circ_center = e.Curve.Center
            # Use lowercase .y here!
            if abs(circ_center.y) < 1e-3: 
                connection_fillets.append(e)

    if connection_fillets:
        try:
            # Keep the fillet small to avoid clashing with the fin edges
            strut_fillet_radius = 0.6
            fin = fin.makeFillet(strut_fillet_radius, connection_fillets)
        except Exception as err:
            print(f"Strut connection fillet failed: {err}")
    
    # --- ADD CIRCULAR BASE TO FIN ---
    foot_radius = 11.4  # Radius of the support circle
    foot_height = 0.2  
    
    # Create the disk at the base of the fin (Z=0)
    # Positioning it at X=thick/2 and Y=width_base/2 to center it under the fin's footprint
    foot = Part.makeCylinder(foot_radius, foot_height)
    foot.translate(App.Vector(thick/2.0, width_base/2.0, 0))
    
    # Fuse the foot to the fin structure
    fin = fin.fuse(foot)
    
    return fin

    

# --- Parameters ---
fin_width_base = 22.5       # How far the fin sticks out and how high it goes
fin_width_top = 10
fin_height = 215.0
fin_thickness = 9 #.4   # Width of the fin
#fin_chamfer = 1.0 # 2,0 #1.5     # Chamfer on the edge touching the calendar
fin_fillet = 3      # Fillet for the outer edges
# ------------------


# --- Placement Logic ---
bbox = obj_base.Shape.BoundBox
cal_width = bbox.XMax - bbox.XMin
inset_frac = 0.013

#x_positions = [bbox.XMin + cal_width * inset_frac, bbox.XMin + cal_width * (1-inset_frac)]
x_positions = [bbox.XMin + spacing*1.5+hole_width,bbox.XMin + spacing*6.5+6*hole_width]
rotations = [0,0]
y_positions = [0,0] #[0.3,-3.7]
gap = 1.5

# Center the fin thickness on the X points
x_offset = fin_thickness / 2



for x,y,rot in zip(x_positions,y_positions,rotations):
    # --- FIN ON THE BACK SIDE (Y-Min) ---
    #fin_back = make_fin(fin_size, fin_thickness, fin_chamfer, fin_fillet)
    # Rotate 180 around Z so the triangle points away from the calendar
    #fin_back.rotate(App.Vector(0,0,0), App.Vector(0,0,1), 180)
    # Move to Y-Min minus the gap
    #fin_back.translate(App.Vector(x + x_offset, bbox.YMin - gap, 0))
    #Part.show(fin_back, "SupportFin_Back")
    #all_parts.append(fin_back)

    # --- FIN ON THE FRONT SIDE (Y-Max) ---
    fin_front = make_fin(fin_width_base, fin_width_top, fin_height, fin_thickness, fin_fillet)
    fin_front.rotate(App.Vector(0,0,0), App.Vector(0,0,1), rot)
    
    # Move to Y-Max plus the gap
    fin_front.translate(App.Vector(x - x_offset, bbox.YMax + gap+y, 0))
    #Part.show(fin_front, "SupportFin_Front")
    #all_parts.append(fin_front)

#print("Fins placed successfully.")

# ==================================================
# FINAL ASSEMBLY
# ==================================================



# 1. Hide everything currently in the document
for obj in doc.Objects:
    if hasattr(obj, "ViewObject"):
        obj.ViewObject.Visibility = False
        

if all_parts:
    print(f"Fusing {len(all_parts)} components...")
    
    # Perform the fusion
    # We take the first shape and fuse all subsequent shapes to it
    fused_shape = all_parts[0].multiFuse(all_parts[1:])
    
    # Show the result
    final_obj = Part.show(fused_shape, "FINAL_PRINT_MODEL")
            
    doc.recompute()
    print("Success! 'FINAL_PRINT_MODEL' is ready for export.")


# 3. Ensure the final one is definitely visible
final_obj.ViewObject.Visibility = True

###

import math

# ==================================================
# FINAL ROTATION AND SIZE CHECK
# ==================================================
print("Applying 45-degree diagonal rotation...")

# 1. Rotate the final object 45 degrees around the Z-axis
# We do this to the final_output object created in the previous step
angle = 45 #0 #45+180
rot = App.Rotation(App.Vector(0, 0, 1), angle)
final_obj.Placement.Rotation = rot.multiply(final_obj.Placement.Rotation)

doc.recompute()

# 2. Calculate the Bounding Box of the rotated shape
# Note: We look at the Shape's BoundBox after the placement is applied
final_bbox = final_obj.Shape.BoundBox

width_x = final_bbox.XMax - final_bbox.XMin
depth_y = final_bbox.YMax - final_bbox.YMin
height_z = final_bbox.ZMax - final_bbox.ZMin

# 3. Print the results for build plate validation
print("-" * 30)
print("FINAL BUILD DIMENSIONS (Rotated 45°):")
print(f"X (Width):  {width_x:.2f} mm")
print(f"Y (Depth):  {depth_y:.2f} mm")
print(f"Z (Height): {height_z:.2f} mm")
print("-" * 30)

# 4. Optional: Create a visual bounding box (wireframe) to see the footprint
# bbox_wire = Part.makeBox(width_x, depth_y, height_z, final_bbox.Min)
# Part.show(bbox_wire, "BuildPlate_Footprint")

# 5. Final Camera Fit
Gui.SendMsgToActiveView("ViewFit")

doc.recompute()
print("Ok!")



if False:
	
	
	# ==================================================
	# FLIP PART AND RE-GROUND TO BED
	# ==================================================
	#print("Flipping part upside down...")
	
	# 1. Apply a 180-degree rotation around the X-axis
	flip_rot = App.Rotation(App.Vector(1, 0, 0), 0) #180)
	obj_base.Placement.Rotation = flip_rot.multiply(obj_base.Placement.Rotation)
	doc.recompute()
	
	# 2. Re-ground the part (Move it so the new bottom is at Z=0)
	# After flipping, the part might be floating or underground.
	new_bbox = obj_base.Shape.BoundBox
	current_z_min = new_bbox.ZMin
	obj_base.Placement.Base.z = obj_base.Placement.Base.z - current_z_min
	
	
	# ... after you flip and ground the calendar ...
	all_parts.append(obj_base.Shape)
	
	
	
	
	# ==================================================
	# ADD MOUSE EARS BASED ON ACTUAL BOTTOM FOOTPRINT
	# ==================================================
	print("Calculating bottom footprint for mouse ears...")
	
	# 1. Define mouse ear parameters
	ear_radius = 5.0  # mm
	ear_height = 0.3   # mm
	
	# 2. Find the absolute bottom of the object
	# Even if it's at Z=0, we slice slightly above (0.1mm) to 
	# ensure we are intersecting the actual solid material.
	z_slice = obj_base.Shape.BoundBox.ZMin + 0.1
	
	# 3. Create a large horizontal plane to slice the model
	# We use a very large plane to ensure it covers the whole calendar
	slice_plane = Part.makePlane(1000, 1000, App.Vector(-500, -500, z_slice), App.Vector(0, 0, 1))
	
	# 4. Perform the "Section" (intersection of the plane and the calendar)
	# This results in a set of edges representing the footprint at that height
	footprint_section = obj_base.Shape.section(slice_plane)
	footprint_bbox = footprint_section.BoundBox
	
	# 5. Locate positions for the ears
	# We use the footprint's X limits and the center of its Y thickness
	x_left = footprint_bbox.XMin
	x_right = footprint_bbox.XMax
	y_center = (footprint_bbox.YMin + footprint_bbox.YMax) / 2
	
	# 6. Create and place the cylinders
	# To make them "Tangent" (touching the edge from the outside):
	# Left ear center = XMin - Radius
	# Right ear center = XMax + Radius
	# Note: For better 3D printing adhesion, many prefer a 2mm overlap.
	# To overlap, you could use (x_left - ear_radius + 2)
	left_center_x = x_left - ear_radius
	right_center_x = x_right + ear_radius
	
	# Create the ear shapes
	left_ear = Part.makeCylinder(ear_radius, ear_height)
	left_ear.translate(App.Vector(left_center_x, y_center, 0))
	
	right_ear = Part.makeCylinder(ear_radius, ear_height)
	right_ear.translate(App.Vector(right_center_x, y_center, 0))
	
	# 7. Add them to the document
	Part.show(left_ear, "MouseEar_Left")
	Part.show(right_ear, "MouseEar_Right")
	
	# ... inside your mouse ear logic ...
	all_parts.append(left_ear)
	all_parts.append(right_ear)
	
	doc.recompute()
	print(f"Ears placed at X: {left_center_x:.2f} and {right_center_x:.2f}")
	
	# ==================================================
	# ADD CONNECTING ANCHOR STRIPS (1ST LAYER)
	# ==================================================
	print("Adding anchor strips between ears and fins...")
	
	
	# We need the centers of the ears and the centers of the fins
	# Left Ear center: (left_center_x, y_center)
	# Right Ear center: (right_center_x, y_center)
	
	# Collect fin centers from the previous placement logic
	# Assuming x_positions = [x_left_fins, x_right_fins]
	left_fin_x = x_positions[0]
	right_fin_x = x_positions[1]
	
	# Y positions for the fins were bbox.YMin - gap and bbox.YMax + gap
	# Center Y for the fins:
	back_fin_y = bbox.YMin - gap
	front_fin_y = bbox.YMax + gap
	
	def create_strip(p1, p2, width, height):
	    """Creates a rounded-end strip and trims the length slightly"""
	    dx = p2.x - p1.x
	    dy = p2.y - p1.y
	    full_dist = math.sqrt(dx**2 + dy**2)
	    radius = width / 2.0
	    
	    # --- The Shortering Logic ---
	    # Subtract 4mm (2mm from each end) to keep it from sticking out too far
	    trim_amount = 2 
	    dist = full_dist - trim_amount
	    
	    # If the distance is too small, prevent errors
	    if dist < 1.0: dist = 1.0
	    # ----------------------------
	
	    # 1. Create the profile (Same as before)
	    p_tl = App.Vector(0, radius, 0)
	    p_tr = App.Vector(dist, radius, 0)
	    p_br = App.Vector(dist, -radius, 0)
	    p_bl = App.Vector(0, -radius, 0)
	    
	    line_top = Part.makeLine(p_tl, p_tr)
	    line_bot = Part.makeLine(p_br, p_bl)
	    arc_right = Part.Arc(p_tr, App.Vector(dist + radius, 0, 0), p_br).toShape()
	    arc_left = Part.Arc(p_bl, App.Vector(-radius, 0, 0), p_tl).toShape()
	    
	    wire = Part.Wire([line_top, arc_right, line_bot, arc_left])
	    face = Part.Face(wire)
	    strip = face.extrude(App.Vector(0, 0, height))
	    
	    # 2. Orient it
	    angle = math.degrees(math.atan2(dy, dx))
	    strip.rotate(App.Vector(0,0,0), App.Vector(0,0,1), angle)
	    
	    # 3. Move it (We shift it forward by half the trim_amount to center it)
	    shift_x = 0*(trim_amount ) * math.cos(math.radians(angle))
	    shift_y = (trim_amount / 2.0) * math.sin(math.radians(angle))
	    strip.translate(App.Vector(p1.x + shift_x, p1.y + shift_y, 0))
	    
	    return strip
	
	# Points for connections
	left_ear_p = App.Vector(left_center_x, y_center, 0)
	right_ear_p = App.Vector(right_center_x, y_center, 0)
	
	# --- Tuning Parameter ---
	# 0.0 = Calendar wall, 1.0 = Far tip of fin
	t = 0.7  # Adjust this to move the connection further back
	# ------------------------
	
	# Define the start and end of the fin base along Y
	# Back Fins
	back_start_y = bbox.YMin - gap
	back_end_y = back_start_y - fin_size
	# Front Fins
	front_start_y = bbox.YMax + gap
	front_end_y = front_start_y + fin_size
	
	# Apply the Convex Combination: Point = (1-t)*Start + t*End
	back_target_y = (1 - t) * back_start_y + t * back_end_y
	front_target_y = (1 - t) * front_start_y + t * front_end_y
	# --- Tuning Parameters ---
	t = 0.8             # Position along the fin
	strip_width = 5.0
	strip_height = 0.3
	ear_offset = 3.0    # Distance to move the strip start away from the calendar center
	# -------------------------
	
	# Points for connections (with offsets to avoid the calendar)
	# For the back strips, move the start point "down" (negative Y)
	left_ear_back_p = App.Vector(left_center_x, y_center - ear_offset, 0)
	right_ear_back_p = App.Vector(right_center_x, y_center - ear_offset, 0)
	
	# For the front strips, move the start point "up" (positive Y)
	left_ear_front_p = App.Vector(left_center_x, y_center + ear_offset, 0)
	right_ear_front_p = App.Vector(right_center_x, y_center + ear_offset, 0)
	
	# 1. Left Side Strips
	s1 = create_strip(left_ear_back_p, App.Vector(left_fin_x, back_target_y, 0), strip_width, strip_height)
	s2 = create_strip(left_ear_front_p, App.Vector(left_fin_x, front_target_y, 0), strip_width, strip_height)
	
	# 2. Right Side Strips
	s3 = create_strip(right_ear_back_p, App.Vector(right_fin_x, back_target_y, 0), strip_width, strip_height)
	s4 = create_strip(right_ear_front_p, App.Vector(right_fin_x, front_target_y, 0), strip_width, strip_height)
	
	all_parts.extend([s1, s2, s3, s4])
	
	print("Anchor strips added to master fusion list.")
	
	

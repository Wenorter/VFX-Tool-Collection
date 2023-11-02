import maya.cmds as cmds
import re
import os

#Global Vars
scroll_list = None
saved_root_path = None
root_path_textfield = None
text_fields = []  
standard_focal_lengths = (12, 14, 16, 18, 21, 25, 27, 32, 35, 40, 50, 65, 75, 100, 135, 150)
standard_fstop_values = (1.3, 2, 2.8, 4, 5.6, 8, 11, 16, 22)
naming_convention = r"^[A-Z]{1,3}_([A-Z]{1}[a-z]+)+$"
export_asset_groups = ["props", "characters", "set", "setPiece"]
import math

def save_root_path():
    global root_path_textfield
    saved_root_path = str(cmds.textFieldGrp(root_path_textfield, query=True, text=True))
    addLog("Root Path set to: " + saved_root_path)
#---------------------------GENERAL CHECKS------------------------------------------------------

def check_naming_convention():
    # Example usage with selected asset in Maya:
    selected_assets = cmds.ls(sl=True, type="transform")  # Assuming you have selected asset objects.
    for asset in selected_assets:
        global naming_convention
        if re.match(naming_convention, asset):
            addLog(f"{asset} matches the naming convention.")
        else:
            addLog(f"{asset} does not match the camelCase naming convention. Example: CameraPerspective")

    pattern = r"^[A-Z]{1,3}_([A-Z]{1}[a-z]+)+$"
    return bool(re.match(pattern, asset))

def check_unknown_nodes():
    no_unknown_nodes = True
    selected_assets = cmds.ls(selection=True, type="transform")

    for asset in selected_assets:
        unknown_nodes = cmds.ls(dag=True, long=True, referencedNodes=True, type="unknown")
        if unknown_nodes:
            for node in unknown_nodes:
                addLog(f"UNUSED NODE in {asset}: {node}")
                no_unknown_nodes = False
        if no_unknown_nodes:
            addLog("PASS: {asset} has no unknown nodes")
    return no_unknown_nodes

def check_nan_values():
    has_naan_values = False
    selected_assets = cmds.ls(sl=True, type="transform")  # Assuming you have selected asset objects.
    
    for asset in selected_assets:
        attributes_to_check = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ"]
        
        for attr in attributes_to_check:
            attr_value = cmds.getAttr(f"{asset}.{attr}")
            if math.isnan(attr_value):
                addLog(f"FAIL: {asset}.{attr} has a NaN value.")
                has_naan_values = True
                return False

    addLog(f"PASS: {asset} has no NaN values")
    return not has_naan_values

def check_node_hierarchy():
    correct_hierarchy = True
    selected_assets = cmds.ls(sl=True, type="transform")  # Assuming you have selected asset objects.
    for asset in selected_assets:
        asset_parents = cmds.listRelatives(asset, parent=True, fullPath=True)
        if asset_parents:
            asset_parent= asset_parents[0].replace('|', "")
            global export_asset_groups
            if asset_parent not in export_asset_groups:
                addLog(f"FAIL: {asset} does not match correct node hierarchy for exports. Supported export groups are: {export_asset_groups}")
                correct_hierarchy = False
            else:
                addLog(f"PASS: {asset} has correct node hierarchy for publishing")
        else:
            addLog(f"FAIL: {asset} does not have a parent group. Supported export parent groups are {export_asset_groups} ")
            correct_hierarchy = False

    return correct_hierarchy

#---------------------------LAYOUT CHECKS----------------------------------------dfd--------------

def cameras_selected():
    result = False
    for each_cam_tf in cmds.ls(sl=True):
        cam_shp = cmds.listRelatives(each_cam_tf, type="camera")
        if cam_shp:
            result = True
    return result

def check_camera_aspect_ratio():
    """
    Check if the camera aperture of selected camera is in a 16:9 aspect ratio.
    """

    if not cameras_selected():
        addLog("INFO: This check only can run on cameras")
        return None

    result = True
    for each_cam_tf in cmds.ls(sl=True):
        cam_shp = cmds.listRelatives(each_cam_tf, type="camera")
        if cam_shp:
            camera_name = cmds.listRelatives(cam_shp[0], parent=True)[0]
            horizontal_aperture = cmds.getAttr(cam_shp[0] + ".horizontalFilmAperture")
            vertical_aperture = cmds.getAttr(cam_shp[0] + ".verticalFilmAperture")
            # Check if camera settings match a specific aspect ratio (16:9)
            if abs(horizontal_aperture / vertical_aperture - 16.0 / 9.0) < 0.01:
                message= f"PASS: {camera_name}: Aspect Ratio is 16:9, or roughly {(horizontal_aperture/vertical_aperture):.2f}"
            else:
                result = False
                message= f"FAIL: {camera_name}: Aspect Ratio is not 16:9. It is {(horizontal_aperture/vertical_aperture):.2f}"

            addLog(message)
    return result

def check_focal_lengths():

    if not cameras_selected():
        addLog("INFO: This check only can run on cameras")
        return None

    result = True
    for each_cam_tf in cmds.ls(sl=True):
        cam_shp = cmds.listRelatives(each_cam_tf, type="camera")
        if cam_shp:
            camera_name = cmds.listRelatives(cam_shp[0], parent=True)[0]
            focal_length = cmds.getAttr(cam_shp[0] + ".focalLength")
            # Check if the focal length is in the list of standardized focal lengths
            global standard_focal_lengths
            if focal_length in standard_focal_lengths:
                message = f"PASS: {camera_name}: Focal Length is standardized ({focal_length})"
            else:
                result = False
                message = f"FAIL: {camera_name}: Focal Length is not standardized ({focal_length})"

            addLog(message) 

    return result

def check_fstop_values():

    if not cameras_selected():
        addLog("INFO: This check only can run on cameras")
        return None
    
    result = True
    for each_cam_tf in cmds.ls(sl=True):
        cam_shp = cmds.listRelatives(each_cam_tf, type="camera")
        if cam_shp:
            camera_name = cmds.listRelatives(cam_shp[0], parent=True)[0]
            f_stop = cmds.getAttr(cam_shp[0] + ".fStop")
            # Check if the F-stop value is in the list of standardized F-stop values
            global standard_fstop_values
            if f_stop in standard_fstop_values:
                message = f"PASS: {camera_name}: F-Stop is standardized ({f_stop})"
            else:
                result = False
                message = f"FAIL: {camera_name}: F-Stop is not standardized ({f_stop})"

            addLog(message) 

    return result

#---------------------------SET PIECE CHECKS------------------------------------------------------

def check_transform_at_origin():
    selected_assets = cmds.ls(selection=True, type="transform")
    transform_at_origin = None
    for asset in selected_assets:
        transform_at_origin = True
        transform_position = cmds.xform(asset, query=True, translation=True, worldSpace=True)
        formatted_position = [round(val, 4) for val in transform_position]
        if formatted_position == [0.0000, 0.0000, 0.0000]:
            message = f"PASS: {asset} is at the origin."
        else:
            message = f"FAIL: {asset} is not at the origin. Position: {formatted_position}"
            transform_at_origin = False
        
        addLog(message)
    return transform_at_origin

def check_pivot_at_origin():
    selected_assets = cmds.ls(selection=True, type="transform")
    pivot_at_origin = None

    for asset in selected_assets:
        pivot_at_origin = True
        pivot = cmds.xform(asset, query=True, piv=True, worldSpace=True)
        formatted_pivot = [round(val, 4) for val in pivot]

        if formatted_pivot == [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]:
            message = f"PASS: {asset} has its pivot at the origin."
        else:
            message = f"FAIL: {asset} does not have its pivot at the origin. Pivot: {formatted_pivot}"
            pivot_at_origin = False

        addLog(message)

    return pivot_at_origin

#---------------------------UI FUNCTIONS------------------------------------------------------

def reset_results():
    global text_fields
    global scroll_list
    print("resetted logs")
    for text_field in text_fields:
        cmds.text(text_field, edit=True, backgroundColor=(0.2667, 0.2667, 0.2667))
    cmds.textScrollList(scroll_list, edit=True, removeAll=True)
    
def run_check(check_function, text_field):
    result = check_function()
    if result == True:
        cmds.text(text_field, edit=True, backgroundColor=(0.56, 0.93, 0.56))
    elif result == False:
        cmds.text(text_field, edit=True, backgroundColor=(0.8, 0.2, 0.2))
    else:
        cmds.text(text_field, edit=True, backgroundColor=(0.2667, 0.2667, 0.2667))
        
def run_all_general_checks(naming_convention_text, node_hierarchy_label, unknown_nodes_label, nan_values_label):
    addLog("-----GENERAL CHECKS-------")
    run_check(check_naming_convention, naming_convention_text)
    run_check(check_node_hierarchy,node_hierarchy_label)
    run_check(check_unknown_nodes, unknown_nodes_label)
    run_check(check_nan_values, nan_values_label)

def run_all_layout_checks(aspect_ratio_text, focal_length_text, fstop_text):
    addLog("-----LAYOUT CHECKS-------")
    run_check(check_camera_aspect_ratio, aspect_ratio_text)
    run_check(check_focal_lengths, focal_length_text)
    run_check(check_fstop_values, fstop_text)

def run_all_setpiece_checks(transform_at_origin_label, pivot_at_origin_label):
    addLog("-----SET PIECE CHECKS-------")
    run_check(check_transform_at_origin, transform_at_origin_label)
    run_check(check_pivot_at_origin, pivot_at_origin_label)

def create_section(section_title, parent):
    return cmds.frameLayout(label=section_title, collapsable=True, collapse=False, parent=parent, marginWidth=10, marginHeight=10)

def addLog(message):
    print("LOG: " + message)
    global scroll_list
    cmds.textScrollList(scroll_list, edit=True, append=[message])
    # Scroll to the last item in the list to show the bottom
    num_items = cmds.textScrollList(scroll_list, query=True, numberOfItems=True)
    if num_items > 0:
        last_item_index = num_items  # Index of the last item
        cmds.textScrollList(scroll_list, edit=True, showIndexedItem=last_item_index)

def create_ui():
    """
    Create the UI for running integrity checks in Maya.
    """

    if cmds.window('Integrity Checker Tool', exists=True):
        cmds.deleteUI('Integrity Checker Tool')

    # Create a window--------------------------------------------------------------------------------------
    window_width = 300
    window_height = 800
    column1_width = 300
    column2_width = 200
    column3_width = 10
    ic_window = cmds.window("Integrity Checker Tool", title="Integrity Checker Tool", width=window_width, height=window_height)
    ic_layout = cmds.columnLayout(adjustableColumn=True)

    # Add a section for the root path input
    create_section("Root Path", ic_window)
    global root_path_textfield
    root_path_textfield = cmds.textFieldGrp(label="Root Path:", columnWidth2=[100, 250])
    cmds.button(label="Save", command=lambda *args: save_root_path())

    #---------------------------GENERAL--------------------------------------------------
    
    create_section("General", ic_window)
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    naming_convention_text = cmds.text(label="Check Asset Naming Convention")
    text_fields.append(naming_convention_text)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_naming_convention, naming_convention_text))
    cmds.setParent('..')  

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    node_hierarchy_label = cmds.text(label="Check Node Hierarchy")
    text_fields.append(node_hierarchy_label)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_node_hierarchy, node_hierarchy_label))
    cmds.setParent('..')  

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    unknown_nodes_label = cmds.text(label="Check Unknown Nodes")
    text_fields.append(unknown_nodes_label)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_unknown_nodes, unknown_nodes_label))
    cmds.setParent('..')  

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    nan_values_label = cmds.text(label="Check Nan Values")
    text_fields.append(nan_values_label)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_nan_values, nan_values_label))
    cmds.setParent('..')  

    cmds.button(label="Run All General Checks", command=lambda *args: run_all_general_checks(naming_convention_text, node_hierarchy_label, unknown_nodes_label, nan_values_label))

    #---------------------------LAYOUT------------------------------------------------------
    create_section("Layout", ic_window)

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    aspect_ratio_text = cmds.text(label=" Check Aspect Ratio 16:9 ")
    text_fields.append(aspect_ratio_text)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_camera_aspect_ratio, aspect_ratio_text))
    cmds.setParent('..')  

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    focal_length_text = cmds.text(label=" Check Focal Lengths ")
    text_fields.append(focal_length_text)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_focal_lengths, focal_length_text))
    cmds.setParent('..')  

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    fstop_text = cmds.text(label=" Check F-Stop Values ")
    text_fields.append(fstop_text)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_fstop_values, fstop_text))
    cmds.setParent('..')  

    cmds.button(label="Run All Layout Checks", command=lambda *args: run_all_layout_checks(aspect_ratio_text, focal_length_text, fstop_text))
    # #---------------------------SET-PIECES--------------------------------------------------
    create_section("Set Pieces", ic_window)    

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    transform_at_origin_label = cmds.text(label=" Check Transform at Origin ")
    text_fields.append(transform_at_origin_label)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_transform_at_origin, transform_at_origin_label))
    cmds.setParent('..')  

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    pivot_at_origin_label = cmds.text(label="Check Pivot at Origin")
    text_fields.append(pivot_at_origin_label)
    cmds.button(label="Run Check",  command=lambda *args: run_check(check_pivot_at_origin, pivot_at_origin_label))
    cmds.setParent('..')  

    cmds.button(label="Run Set Piece Checks", command=lambda *args: run_all_setpiece_checks(transform_at_origin_label, pivot_at_origin_label))

    # Show the window--------------------------------------------------------------------------------------
    cmds.showWindow(ic_window)

    # Logs---------------------------------------------------------------------------------------------------
    title_label = cmds.text(label="Result Logs")
    global scroll_list
    scroll_list = cmds.textScrollList(
    numberOfRows=10,  # Set the number of visible rows
    allowMultiSelection=True,  # Allow multiple item selection
    width=300,
    height=300,
    append=[],  # Add items to the list
    parent=ic_layout
    )
    
    cmds.button(label="Reset Results", command='reset_results()', parent=ic_layout)

create_ui()
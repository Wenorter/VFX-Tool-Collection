import maya.cmds as cmds
import re
import os

#Global Vars
scroll_list = None
root_display = None
root_folder = ""
text_fields = []  
standard_focal_lengths = (12, 14, 16, 18, 21, 25, 27, 32, 35, 40, 50, 65, 75, 100, 135, 150)
standard_fstop_values = (1.3, 2, 2.8, 4, 5.6, 8, 11, 16, 22)
naming_convention = r"^[A-Z]{1,3}_([A-Z]{1}[a-z]+)+$"
export_asset_groups = ["props", "characters", "set", "setPiece"]
import math

#---------------------------GENERAL CHECKS------------------------------------------------------

def check_naming_convention():
    error_nodes = []
    # Get all transform nodes in the scene
    transform_nodes = cmds.ls(type="transform")
    for asset in transform_nodes:
        global naming_convention
        if asset not in export_asset_groups:
            if not re.match(naming_convention, asset):
                passed = False
                error_nodes.append(asset)
    
    if not passed:
        addLog(f"FAIL: Naming Convention Check. Error Nodes: {error_nodes}")
    
    return passed

def check_unknown_nodes():
    passed = True
    unknown_nodes = cmds.ls(type="unknown")
    if unknown_nodes:
        passed = False
    
    if not passed:
        addLog(f"FAIL: There are unknown nodes. Error Nodes: {unknown_nodes}")

    return passed

def check_nan_values():
    passed = True
    transform_assets = cmds.ls(type="transform")
    error_nodes = []
    
    for asset in transform_assets:
        attributes_to_check = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ"]
        
        for attr in attributes_to_check:
            attr_value = cmds.getAttr(f"{asset}.{attr}")
            if math.isnan(attr_value):
                error_nodes.append(f"{asset}.{attr}")
                passed = False

    if not passed:
        addLog(f"FAIL: {error_nodes} has NaN value")

    return passed

def check_node_hierarchy():
    global export_asset_groups
    passed = True
    assets = cmds.ls(type="transform")  # Assuming you have selected asset objects.
    error_nodes = []
    for asset in assets:
        if asset not in ["front","top","side","persp"]: #not default camera
            asset_parents = cmds.listRelatives(asset, parent=True, fullPath=True)
            if asset_parents:
                secondary_parents = cmds.listRelatives(asset_parents, parent=True, fullPath=True)
                if not secondary_parents:   #if group is top level
                    asset_parent= asset_parents[0].replace('|', "")
                    if (asset_parent not in export_asset_groups):
                        addLog(f"FAIL: Node Hierarhcy of {asset} does not match correct export groups. Supported: {export_asset_groups}")
                        error_nodes.append(asset)
                        passed = False
            else:
                #if no asset parents, check if a correct group
                if asset.replace('|', "") not in export_asset_groups:
                    addLog(f"FAIL: Node Hierarchy of {asset} does not have a parent group. Supported: {export_asset_groups} ")
                    error_nodes.append(asset)
                    passed = False

    return passed

def check_reference_errors():
    error_nodes = []
    passed = True
    
    unloaded_reference_files = [file for file in cmds.file(reference=True, q=True) if not cmds.referenceQuery(file, isLoaded=True)]
    if unloaded_reference_files:
        passed = False
        error_nodes = unloaded_reference_files

    if not passed:
        addLog(f"FAIL: reference errors detected. error nodes: {error_nodes}")

    return passed

def check_reference_versions():
    global root_folder
    passed = True

    if not root_folder:
        addLog("ERROR: No Root Folder Specified")
        passed = False
    else:
        for reference_file_path in [file for file in cmds.file(reference=True, q=True) if cmds.referenceQuery(file, isLoaded=True)]:
            reference_filename = os.path.basename(reference_file_path)

            directory_path = os.path.dirname(reference_file_path)
            full_path = str(directory_path)
            filenames_in_directory = [os.path.basename(path) for path in os.listdir(full_path)]
            newest_version = max(filenames_in_directory)

            if (reference_filename < newest_version):
                addLog(f"NEW VERSION ALERT: {newest_version}>>{reference_filename}")
                passed = False
    
    return passed

#---------------------------LAYOUT CHECKS----------------------------------------dfd--------------

def get_camera_relatives():
    relatives = []
    for each_cam_tf in cmds.ls():
       cam_shp = cmds.listRelatives(each_cam_tf, type="camera")
       if cam_shp:
           camera_name = cmds.listRelatives(cam_shp[0], parent=True)[0]
           if camera_name not in ['persp', 'top', 'front', 'side']:
               relatives.append(cam_shp)
    
    return relatives

def check_camera_aspect_ratio():
    """
    Check if the camera aperture of selected camera is in a 16:9 aspect ratio.
    """
    passed = True
    error_nodes = []

    for cam_shp in get_camera_relatives():
        camera_name = cmds.listRelatives(cam_shp[0], parent=True)[0]
        horizontal_aperture = cmds.getAttr(cam_shp[0] + ".horizontalFilmAperture")
        vertical_aperture = cmds.getAttr(cam_shp[0] + ".verticalFilmAperture")

        if not(abs(horizontal_aperture / vertical_aperture - 16.0 / 9.0) < 0.01):
            passed=False
            error_nodes.append(camera_name)

    if not passed:
        addLog(f"FAIL: Aspect Ratio is not 16:9, Error Nodes: {error_nodes}")
    return passed

def check_focal_lengths():
    passed = True
    error_nodes = []
    global standard_focal_lengths

    for cam_shp in get_camera_relatives():
        camera_name = cmds.listRelatives(cam_shp[0], parent=True)[0]
        focal_length = cmds.getAttr(cam_shp[0] + ".focalLength")
        if not(focal_length in standard_focal_lengths):
            passed = False
            error_nodes.append(camera_name)

    if not passed:
        addLog(f"FAIL: Focal Lengths not standardized, Error Nodes: {error_nodes}")
    return passed

def check_fstop_values():
    passed = True
    error_nodes = []
    global standard_fstop_values

    for cam_shp in get_camera_relatives():
        camera_name = cmds.listRelatives(cam_shp[0], parent=True)[0]
        focal_length = cmds.getAttr(cam_shp[0] + ".fStop")
        if not(focal_length in standard_fstop_values):
            passed = False
            error_nodes.append(camera_name)

    if not passed:
        addLog(f"FAIL: FStops not standardised, Error Nodes: {error_nodes}")
    return passed

#---------------------------SET PIECE CHECKS------------------------------------------------------

def check_transform_at_origin():
    passed = True
    error_nodes = []
    try:
        assets = cmds.ls(sl=True)
        if assets:
            for asset in assets:
                transform_position = cmds.xform(asset, query=True, translation=True, worldSpace=True)
                formatted_position = [round(val, 4) for val in transform_position]
                if not (formatted_position == [0.0000, 0.0000, 0.0000]):
                    passed=False
                    error_nodes.append(asset)
    except:
        addLog("This node has no transform/pivot")

    if not passed:
        addLog(f"FAIL: Transform is not at origin. Error Nodes: {error_nodes}")

    return passed

def check_pivot_at_origin():
    passed = True
    error_nodes = []
    try:
        assets = cmds.ls(sl=True)

        if assets:
            for asset in assets:
                pivot = cmds.xform(asset, query=True, piv=True, worldSpace=True)
                formatted_pivot = [round(val, 4) for val in pivot]

                if not formatted_pivot == [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]:
                    passed=False
                    error_nodes.append(asset)
    
    except:
        addLog("This node has no transform/pivot")

    if not passed:
        addLog(f"FAIL: Transform pivot not at origin. Error Nodes: {error_nodes}")

    return passed

#---------------------------UI FUNCTIONS------------------------------------------------------

def pick_root():
    global root_folder
    global root_display
    root_folder = cmds.fileDialog2(dialogStyle=2, fileMode=3)
    cmds.textScrollList(root_display, edit=True, append=root_folder)

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

    return result
        
def run_all_general_checks(naming_convention_text, node_hierarchy_label, unknown_nodes_label, nan_values_label, reference_errors_label, reference_versions_label):
    reset_results()
    run_check(check_naming_convention, naming_convention_text)
    run_check(check_node_hierarchy,node_hierarchy_label)
    run_check(check_unknown_nodes, unknown_nodes_label)
    run_check(check_nan_values, nan_values_label)
    run_check(check_reference_errors, reference_errors_label)
    run_check(check_reference_versions, reference_versions_label)


def run_all_layout_checks(aspect_ratio_text, focal_length_text, fstop_text):
    reset_results()
    run_check(check_camera_aspect_ratio, aspect_ratio_text)
    run_check(check_focal_lengths, focal_length_text)
    run_check(check_fstop_values, fstop_text)

def run_all_setpiece_checks(transform_at_origin_label, pivot_at_origin_label):
    reset_results()
    run_check(check_transform_at_origin, transform_at_origin_label)
    run_check(check_pivot_at_origin, pivot_at_origin_label)

def create_section(section_title, parent):
    return cmds.frameLayout(label=section_title, collapsable=True, collapse=False, parent=parent, marginWidth=10, marginHeight=10)

def create_errornode_bar(parent):
    return cmds.textScrollList(
    numberOfRows=1,  
    allowMultiSelection=True,
    width=300,
    height=20,
    parent=parent
    )

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

    # Create a window--------------------------------------------------------------------------------------
    window_width = 300
    window_height = 800
    column1_width = 200
    column2_width = 100
    column3_width = 10
    if (cmds.window("IntegrityChecker_Window", q=True, exists=True)):
        cmds.deleteUI("IntegrityChecker_Window", window=True)

    ic_window = cmds.window("IntegrityChecker_Window", title="Integrity Checker", w = window_width, h = window_height)
    ic_layout = cmds.columnLayout(adjustableColumn=True)

    global text_fields
    text_fields = []  

    #---------------------------GENERAL--------------------------------------------------
    create_section("General", ic_window)
    cmds.button(label="Pick Root Folder", command='pick_root()')
    global root_display
    root_display = cmds.textScrollList(
    numberOfRows=1,  # Set the number of visible rows
    width=100,
    height=30,
    append=[]
    )
    cmds.text("Runs on all nodes in the scene")    

    asset_naming_row = cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    naming_convention_text = cmds.text(label="Check Asset Naming Convention")
    text_fields.append(naming_convention_text)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_naming_convention, naming_convention_text))
    cmds.setParent('..')  

    node_hierarchy_row = cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    node_hierarchy_label = cmds.text(label="Check Node Hierarchy")
    text_fields.append(node_hierarchy_label)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_node_hierarchy, node_hierarchy_label))
    cmds.setParent('..')  

    unknown_nodes_row = cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    unknown_nodes_label = cmds.text(label="Check Unknown Nodes")
    text_fields.append(unknown_nodes_label)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_unknown_nodes, unknown_nodes_label))
    cmds.setParent('..')  

    check_nan_row = cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    nan_values_label = cmds.text(label="Check Nan Values")
    text_fields.append(nan_values_label)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_nan_values, nan_values_label, check_nan_row))
    cmds.setParent('..')  

    reference_errors_row = cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    reference_errors_label = cmds.text(label="Check Reference Errors")
    text_fields.append(reference_errors_label)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_reference_errors, reference_errors_label))
    cmds.setParent('..')  

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    reference_versions_label = cmds.text(label="Check Reference Versions")
    text_fields.append(reference_versions_label)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_reference_versions, reference_versions_label))
    cmds.setParent('..')  

    cmds.button(label="Run All General Checks", command=lambda *args: run_all_general_checks(naming_convention_text, node_hierarchy_label, unknown_nodes_label, nan_values_label, reference_errors_label, reference_versions_label))

    #---------------------------LAYOUT------------------------------------------------------
    create_section("Layout", ic_window)
    cmds.text("Runs on all non-startup cameras in the scene")    

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
    create_section("Transform", ic_window)

    cmds.text("Only runs only on selected Nodes")    

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

    cmds.button(label="Run Transform Checks", command=lambda *args: run_all_setpiece_checks(transform_at_origin_label, pivot_at_origin_label))

    # Show the window--------------------------------------------------------------------------------------
    cmds.showWindow(ic_window)

    # Logs---------------------------------------------------------------------------------------------------
    cmds.text(label="Error Details")
    global scroll_list
    scroll_list = cmds.textScrollList(
    numberOfRows=10,  # Set the number of visible rows
    allowMultiSelection=True,  # Allow multiple item selection
    width=300,
    height=300,
    append=[],  # Add items to the list
    parent=ic_layout
    )
    
    cmds.button(label="Clear Logs", command='reset_results()', parent=ic_layout)

create_ui()
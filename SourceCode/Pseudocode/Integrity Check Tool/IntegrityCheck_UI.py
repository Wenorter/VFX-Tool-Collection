import maya.cmds as cmds
import re

#Global Vars
scroll_list = None

text_fields = []  # Replace with your text fields
standard_focal_lengths = (12, 14, 16, 18, 21, 25, 27, 32, 35, 40, 50, 65, 75, 100, 135, 150)
standard_fstop_values = (1.3, 2, 2.8, 4, 5.6, 8, 11, 16, 22)
naming_convention = r"^[A-Z]{1,3}_([A-Z]{1}[a-z]+)+$"

#---------------------------GENERAL CHECKS------------------------------------------------------

def check_naming_convention():
    # Example usage with selected asset in Maya:
    selected_assets = cmds.ls(sl=True, type="transform")  # Assuming you have selected asset objects.
    for asset in selected_assets:
        asset_name = asset
        global naming_convention
        if re.match(naming_convention, asset_name):
            addLog(f"{asset_name} matches the naming convention.")
        else:
            addLog(f"{asset_name} does not match the naming convention. Example: A_CameraPerspective")

    pattern = r"^[A-Z]{1,3}_([A-Z]{1}[a-z]+)+$"
    return bool(re.match(pattern, asset_name))

def check_unknown_nodes():
    selected_assets = cmds.ls(selection=True, type="transform")

    for asset in selected_assets:
        cmds.select(asset, replace=True)

        unused_nodes = cmds.ls(dag=True, long=True, referencedNodes=True, intermediates=True)
        if unused_nodes:
            for node in unused_nodes:
                addLog(f"UNUSED NODE in {asset}: {node}")

    return any(len(cmds.ls(type="unknown")) for asset in selected_assets)

#---------------------------LAYOUT CHECKS------------------------------------------------------

def check_camera_aspect_ratio():
    """
    Check if the camera aperture of selected camera is in a 16:9 aspect ratio.
    """
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
#---------------------------UI FUNCTIONS------------------------------------------------------

def reset_text_fields_background_color():
    global text_fields
    print(text_fields)
    for text_field in text_fields:
        cmds.text(text_field, edit=True, backgroundColor=(0.2667, 0.2667, 0.2667))

def run_check(check_function, text_field):
    result = check_function()
    if result == True:
        cmds.text(text_field, edit=True, backgroundColor=(0.56, 0.93, 0.56))
    else:
        cmds.text(text_field, edit=True, backgroundColor=(0.8, 0.2, 0.2))
        
def create_section(section_title, parent):
    return cmds.frameLayout(label=section_title, collapsable=True, collapse=False, parent=parent, marginWidth=10, marginHeight=10)

def addLog(message):
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
    ic_window = cmds.window("Integrity Checker Tool", title="Integrity Checker Tool", width=window_width, height=window_height)
    ic_layout = cmds.columnLayout(adjustableColumn=True)

    #---------------------------GENERAL---------------------------------------------------
    column1_width = 170
    column2_width = 150
    column3_width = 100
    
    create_section("General", ic_window)
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    naming_convention_text = cmds.text(label="Check Asset Naming Convention")
    cmds.button(label="Run Check", command=lambda *args: run_check(check_naming_convention, naming_convention_text))
    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    cmds.text(label="Check Node Hierarchy")
    cmds.button(label="Run Check", command='placeholder()')
    cmds.setParent('..')  # End the rowLayout

    # cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    # cmds.text(label="Check for NaN Values")
    # cmds.button(label="Run Check", command='placeholder()')

    # cmds.setParent('..')  # End the rowLayout

    #---------------------------LAYOUT------------------------------------------------------
    create_section("Layout", ic_window)

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    aspect_ratio_text = cmds.text(label=" Check Aspect Ratio 16:9 ")
    text_fields.append(aspect_ratio_text)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_camera_aspect_ratio, aspect_ratio_text))
    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    focal_length_text = cmds.text(label=" Check Focal Lengths ")
    text_fields.append(focal_length_text)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_focal_lengths, focal_length_text))
    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    fstop_text = cmds.text(label="Check F-Stop Values")
    text_fields.append(fstop_text)
    cmds.button(label="Run Check", command=lambda *args: run_check(check_fstop_values, fstop_text))
    cmds.setParent('..')  # End the rowLayout

    # #---------------------------SET-PIECES--------------------------------------------------
    # create_section("Set Pieces", ic_window)    

    # cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    # cmds.text(label="Check Aspect Ration 16:9")
    # cmds.button(label="Run Check", command='placeholder()')
    # cmds.setParent('..')  # End the rowLayout

    # cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    # cmds.text(label="Check Focal Lengths")
    # cmds.button(label="Run Check", command='placeholder()')
    # cmds.setParent('..')  # End the rowLayout

    # #---------------------------SET---------------------------------------------------------
    # create_section("Set", ic_window)

    # cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    # cmds.text(label="Transform at Origin")
    # cmds.button(label="Run Check", command='placeholder()')
    # cmds.setParent('..')  # End the rowLayout

    # cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    # cmds.text(label="Pivot at Origin")
    # cmds.button(label="Run Check", command='placeholder()')
    # cmds.setParent('..')  # End the rowLayout

    # Show the window--------------------------------------------------------------------------------------
    cmds.showWindow(ic_window)

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.text(label="Transform at Origin")
    cmds.button(label="Run Check", command='placeholder()')
    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.text(label="Pivot at Origin")
    cmds.button(label="Run Check", command='placeholder()')
    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.text(label="Set Piece References \n up to date")
    cmds.button(label="Run Check", command='placeholder()')
    cmds.setParent('..')  # End the rowLayout

    # Logs---------------------------------------------------------------------------------------------------
    title_label = cmds.text(label="Results")
    global scroll_list
    scroll_list = cmds.textScrollList(
    numberOfRows=10,  # Set the number of visible rows
    allowMultiSelection=True,  # Allow multiple item selection
    width=300,
    height=300,
    append=[],  # Add items to the list
    parent=ic_layout
    )
    
    cmds.button(label="Reset Results", command='reset_text_fields_background_color()')

create_ui()
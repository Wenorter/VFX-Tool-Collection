import maya.cmds as cmds

#Global Vars
scroll_list = None

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
    cmds.checkBox(label="Check Unused Nodes")
    cmds.button(label="Run Check", command='placeholder()')


    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    cmds.checkBox(label="Check Node Hierarchy")
    cmds.button(label="Run Check", command='placeholder()')
    

    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    cmds.checkBox(label="Check for NaN Values")
    cmds.button(label="Run Check", command='placeholder()')

    cmds.setParent('..')  # End the rowLayout

    #---------------------------LAYOUT------------------------------------------------------
    create_section("Layout", ic_window)

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.checkBox(label="Check Aspect Ratio 16:9")
    cmds.button(label="Run Check", command=lambda *args: addLog("pass" if check_camera_aspect_ratio() else "fail"))
    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.checkBox(label="Check Focal Lengths")
    cmds.button(label="Run Check", command='placeholder()')
    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.checkBox(label="Check F-Stop Values")
    cmds.button(label="Run Check", command='placeholder()')
    cmds.setParent('..')  # End the rowLayout

    #---------------------------SET-PIECES--------------------------------------------------
    create_section("Set Pieces", ic_window)    

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.checkBox(label="Check Aspect Ration 16:9")
    cmds.button(label="Run Check", command='placeholder()')
    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.checkBox(label="Check Focal Lengths")
    cmds.button(label="Run Check", command='placeholder()')
    cmds.setParent('..')  # End the rowLayout

    #---------------------------SET---------------------------------------------------------
    create_section("Set", ic_window)

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.checkBox(label="Transform at Origin")
    cmds.button(label="Run Check", command='placeholder()')
    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.checkBox(label="Pivot at Origin")
    cmds.button(label="Run Check", command='placeholder()')
    cmds.setParent('..')  # End the rowLayout

    # Show the window--------------------------------------------------------------------------------------
    cmds.showWindow(ic_window)

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.checkBox(label="Transform at Origin")
    cmds.button(label="Run Check", command='placeholder()')
    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.checkBox(label="Pivot at Origin")
    cmds.button(label="Run Check", command='placeholder()')
    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=2, columnWidth2=(column1_width, column2_width))
    cmds.checkBox(label="Set Piece References \n up to date")
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

create_ui()
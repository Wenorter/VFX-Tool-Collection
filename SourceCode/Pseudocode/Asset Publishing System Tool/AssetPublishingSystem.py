# Script Name: Save/Publish Tool for Autodesk Maya
# Description: This tool provides a way for artists to save and publish their work in a way that
#automates the naming of the file and where the file/s are stored.

import os
import re
import maya.cmds as cmds
from functools import partial

scroll_list = None
naming_convention = r"^[A-Z]{1,3}_([A-Z]{1}[a-z]+)+$"

scene_types = ["Asset", "Sequence"]
asset_types = ["setPiece", "set", "prop", "character"]
seq_types = ["animation", "layout", "light"]

#=======================================          
#----------------DEFS-------------------f
#=======================================

#Function for saving file assets as a .MB cache
#Function to get value of a text field
    
def saveFiles():
      
    #Save path is getting assigned from a Current Save Directory Textfield
    save_dir = getTextFieldValue(save_text_field)
    print("CURRENT SAVE PATH: " + save_dir)
    
    if save_dir != "":
        
        save_dir = save_dir + "/assets" 
                                 
        for asset_type in asset_types:
            print("Exporting asset type: ", asset_type)
            addLog("Exporting asset type: " + asset_type)
            asset_group = "|" + asset_type
            
            if cmds.objExists(asset_group):                
                print("Selected object exist")
                asset_roots = cmds.listRelatives(asset_group, children=True, fullPath=True)
                
                for asset in asset_roots:
                    asset_name = asset.split("|")[-1].split(":")[-1]  # Get the object name without the namespace
                    export_dir = "{0}/{1}/{2}".format(save_dir, asset_type, asset_name)
                    print("Asset Name: ", asset_name)
                    file_name = "{0}_layout_v{1}.mb".format(asset_name, str(GetNextVersionNumber(asset_name, asset_type)).zfill(3))                   
                    
                    print("Export directory: ", export_dir)  
                    #if folder doesn't exist create it                                                                                                 
                    try:
                        os.makedirs(export_dir)               
                    except OSError:
                        print(export_dir + " ALREADY EXISTS!")  
                    
                    #Maya Binary Saving
                    export_file = export_dir + "/" + file_name       
                    cmds.file(export_file, force=True, type="mayaBinary", preserveReferences=True, exportSelected=True)
                    print("Exporting Maya Binary Done.")
                    addLog("Exporting Maya Done.")
                cmds.confirmDialog(title="Finished Saving Assets", message="Exporting .MB File Done.\nFile saved at: " + export_file)                       
                                                                                                 
            else:
                print("Asset group doesn't exist.")               
    else:
        print("Directory textfield is empty! Please set root directory first.")
        addLog("Directory textfield is empty! Please set root directory first.")        

#Functions for publishing file assets as .FBX, .ABC or .MB
def publishFiles():
    
    #Publish path is getting assigned from a Current Save Directory Textfield
    publish_dir = getTextFieldValue(publish_text_field)
    print("CURRENT PUBLISH PATH: " + publish_dir)

    if publish_dir != "":
        
        publish_dir = publish_dir + "/assets" 
                                 
        for asset_type in asset_types:
            print("Exporting asset type: ", asset_type)
            addLog("Exporting asset type: " + asset_type)
            asset_group = "|" + asset_type
            
            if cmds.objExists(asset_group):                
                print("Selected object exist")
                asset_roots = cmds.listRelatives(asset_group, children=True, fullPath=True)
                
                for asset in asset_roots:
                    asset_name = asset.split("|")[-1].split(":")[-1]  # Get the object name without the namespace
                    export_dir = "{0}/{1}/{2}".format(publish_dir, asset_type, asset_name)
                    print("Asset Name: ", asset_name)
                    file_name = "{0}_layout_v{1}.mb".format(asset_name, str(GetNextVersionNumber(asset_name, asset_type)).zfill(3))                   
                    
                    print("Export directory: ", export_dir) 
                    
                    #Maya Binary publishing 
                    #if folder doesn't exist create it        
                    try:
                        os.makedirs(export_dir + "/cache")               
                    except OSError:
                        print(export_dir + "/cache" + " ALREADY EXISTS!")                  
                                                       
                    export_file = export_dir + "/cache/" + file_name                                                 
                    cmds.file(export_file, force=True, type="mayaBinary", preserveReferences=True, exportSelected=True)
                    #cmds.confirmDialog(title="Finished Publishing Assets", message="Exporting .MB File Done.\nFile saved at: " + export_file)    
                     
                    #Alembic Publishing 
                    file_name = "{0}_layout_v{1}.abc".format(asset_name, str(GetNextVersionNumber(asset_name, asset_type)).zfill(3))   
                    try:
                        os.makedirs(export_dir + "/alembic")               
                    except OSError:
                        print(export_dir + "/alembic" + " ALREADY EXISTS!") 
                    
                    export_file = export_dir + "/alembic/" + file_name                                                                  
                    alembic_args = [
                    '-renderableOnly',
                    '-file ' + export_file,
                    '-uvWrite',
                    '-writeFaceSets',
                    '-worldSpace',
                    '-writeVisibility',
                    '-dataFormat ogawa',
                    '-root ' + asset,
                    '-fr %d %d' % (cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True))
                    ]
                    print(alembic_args)
                    cmds.AbcExport(j = " ".join(alembic_args))
                    #cmds.confirmDialog(title="Finished Publishing Assets", message="Exporting .ABC File Done.\nFile saved at: " + export_file)    
                    
                    #FBX Publishing
                    file_name = "{0}_layout_v{1}.fbx".format(asset_name, str(GetNextVersionNumber(asset_name, asset_type)).zfill(3))    
                    try:
                        os.makedirs(export_dir + "/fbx")               
                    except OSError:
                        print(export_dir + "/fbx" + " ALREADY EXISTS!")
                                     
                    export_file = export_dir + "/fbx/" + file_name     
                    cmds.file(export_file, force=True, options="v=0;", type="FBX export", pr=True,  ea=True)
                    #cmds.confirmDialog(title="Finished Publishing Assets", message="Exporting .FBX File Done.\nFile saved at: " + export_file)                 
                
                cmds.confirmDialog(title="Finished Publishing Assets", message="Exporting .MB/.ABC/.FBX File Done.\nFile saved at: " + export_dir)                         
                print("Exporting Maya Binary Done.")
                addLog("Exporting Maya Done.")
                print("Publishing Alembic Assets Done.")
                addLog("Publishing Alembic Assets Done.")    
                print("Publishing FBX Assets Done.")
                addLog("Publishing FBX Assets Done.")                 
                                                                                                                                                             
            else:
                print("Asset group doesn't exist.")               
    else:
        print("Directory textfield is empty! Please set root directory first.")
        addLog("Directory textfield is empty! Please set root directory first.")            
                

def GetLatestVersionNumber(asset_name, asset_type):
    dir = "{0}/{1}/{2}".format(save_dir, asset_type, asset_name)
    found = False
    count = 1
    while found == False:
        if not os.path.isfile(dir + "/{0}_layout_v{1}.abc".format(asset_name, str(count).zfill(3))):
            found = True
            count = count - 1
        else:
            count = count + 1
    return count

def GetNextVersionNumber(asset_name, asset_type):
    return GetLatestVersionNumber(asset_name, asset_type) + 1

#=======================================          
#------------------UI-------------------
#=======================================
toolName = 'savePublishTool'
#----------------UI Defs----------------
       
#Function to create section of UI layout
def create_section(section_title, parent):
    return cmds.frameLayout(label=section_title, collapsable=True, collapse=True, parent=parent, marginWidth=10, marginHeight=10)
           
#Function to set the desired scene type of assets        
def setSceneType(scene_type_menu, asset_type_menu):
    # Get the selected value from the optionMenu
    scene_type = cmds.optionMenu(scene_type_menu, query=True, value=True)
    # Check if the selected value is not "Select Scene Type"
    if scene_type != "Select Scene Type":
        scene_type = str(scene_type)
        print("Test Publish Scene")
        if scene_type == "Asset":
            #resetting the option menu to clear items 
            updateOptionMenu(asset_type_menu, asset_types) 
            
        if scene_type == "Sequence":
           #resetting the option menu to clear items
           updateOptionMenu(asset_type_menu, seq_types)
            
        message = f"Scene Type is set to {scene_type}"
        addLog(message)
 
#Function to update opdion menu
def updateOptionMenu(option_type_menu, var_types):
    cmds.optionMenu(option_type_menu, edit=True, deleteAllItems=True)
    cmds.menuItem(label="Select Asset/Seq Type")  
    [cmds.menuItem(label=str(var_type)) for var_type in var_types]
    print("Update option menu: " + option_type_menu)              
    cmds.optionMenu(option_type_menu, edit=True, changeCommand=lambda x: setAssetType(option_type_menu))  
             
#Function to set the desired asset type of publish assets        
def setAssetType(asset_type_menu):
    # Get the selected value from the optionMenu
    asset_type = cmds.optionMenu(asset_type_menu, query=True, value=True)
    # Check if the selected value is not "Choose Asset Type"
    if asset_type != "Select Asset/Seq Type":
        asset_type = str(asset_type)                         
        message = f"Asset/Seq is set to {asset_type}"
        addLog(message)
    
#Function for adding messages to the log scroll list   
def addLog(message):
    cmds.textScrollList(log_scroll_list, edit=True, append=[message])
    # Scroll to the last item in the list to show the bottom
    num_items = cmds.textScrollList(log_scroll_list, query=True, numberOfItems=True)
    if num_items > 0:
        last_item_index = num_items 
        cmds.textScrollList(log_scroll_list, edit=True, showIndexedItem=last_item_index)

#Function for outputing files to the publish list 
def addSaveItem(item):
    cmds.textScrollList(save_scroll_list, edit=True, append=[item])
    num_items = cmds.textScrollList(save_scroll_list, query=True, numberOfItems=True)
    if num_items > 0:
        last_item_index = num_items  
        cmds.textScrollList(save_scroll_list, edit=True, showIndexedItem=last_item_index)
              
#Function for outputing files to the save list 
def addSaveListItems(save_dir):
    saveFileList = []
    saveFileList.clear() #clear list
    clearTextScrollList(save_scroll_list) #clear scroll list
    
    for file_path in os.listdir(save_dir):
        # check if current file_path is a file
        if os.path.isfile(os.path.join(save_dir, file_path)):
            # add filename to list
            saveFileList.append(file_path)                       
    i = 0  
    while i < len(saveFileList):
        addSaveItem(saveFileList[i])
        i = i + 1       
    
#Function for outputing files to the publish list 
def addPublishItem(item):
    cmds.textScrollList(publish_scroll_list, edit=True, append=[item])
    num_items = cmds.textScrollList(save_scroll_list, query=True, numberOfItems=True)
    if num_items > 0:
        last_item_index = num_items  
        cmds.textScrollList(publish_scroll_list, edit=True, showIndexedItem=last_item_index)
        
#Function for outputing files to the save list 
def addPublishListItems(publish_dir):
    publishFileList = []
    publishFileList.clear() #clear list
    clearTextScrollList(publish_scroll_list) #clear scroll list
    
    for file_path in os.listdir(publish_dir):
        # check if current file_path is a file
        if os.path.isfile(os.path.join(publish_dir, file_path)):
            # add filename to list
            publishFileList.append(file_path)
                        
    i = 0  
    while i < len(publishFileList):
        addPublishItem(publishFileList[i])
        i = i + 1       
        
#Function for getting value out of text field
def getTextFieldValue(text_field):
    value = cmds.textField(text_field, query=True, text=True)
    return value
           
#Function to update textfield
def updateTextField(text_field, value):
    print("Clear text field: " + text_field + " " + str(value))
    cmds.textField(text_field, edit=True, text=str(value))
    
#Function to update textfield
def updateTextField(text_field, value):
    print("Clear text field: " + text_field + " " + str(value))
    cmds.textField(text_field, edit=True, text=str(value))
             
#Function for cleaning any scroll list
def clearTextScrollList(scroll_list):
    print("Clear scroll list " + scroll_list)
    cmds.textScrollList(scroll_list, edit=True, removeAll=True)
    
#Function to open file dialog when setting root directory
def open_file_dialog():
    root_dir = cmds.fileDialog2(fileMode=3, caption="Select Root Directory", okCaption="Set Directory")
    if root_dir:
        root_dir = root_dir[0]
        
        print("Setting Directory: " + root_dir) #returning string of directory
        addLog("Setting Directory: " + root_dir)
        updateTextField(root_text_field, root_dir)
        
        global save_dir
        save_dir = root_dir + "/asset_wips/saved"
        print("Setting save directory: " + save_dir)
        addLog("Setting save directory: " + save_dir)  
        updateTextField(save_text_field, save_dir)
        addSaveListItems(save_dir)
        
        global publish_dir
        publish_dir = root_dir + "/asset_final/published"
        print("Setting publish directory: " + publish_dir)
        addLog("Setting publish directory: " + publish_dir)
        updateTextField(publish_text_field, publish_dir)  
        addPublishListItems(publish_dir)      
        
    else:
        cmds.error("Root directory not selected.")
        raise Exception("Root directory not selected.")
            
#--------------UI Init------------------
def createUI():
    if cmds.window(toolName, exists = True):
        cmds.deleteUI(toolName)

    window_width = 400
    window_height = 600

    column1_width = 150 
    column2_width = 200 
    column3_width = 250 

    color_grey = [0.3, 0.3, 0.3]
#-----------Window Create---------------

    #Window
    ic_window = cmds.window(
        toolName, 
        title = "Save Publish Tool for Autodesk Maya", 
        width = window_width, 
        height = window_height
        )
    #Layout
    ic_layout = cmds.columnLayout(adjustableColumn = True) 
    
#------------Init Tool Header--------------------
 
    cmds.separator(style="single", height=15, width = window_width) 
    cmds.text(label = 'Asset Save/Publish Tool for Autodesk Maya', backgroundColor = color_grey, 
        font = "boldLabelFont", align = 'center', width = window_width) 
    cmds.text(label='Saves, Publishes and automates file naming of assets', backgroundColor = color_grey, 
        font = "smallBoldLabelFont", align = 'center', width = window_width)
    cmds.separator(style="single", height=15, width = window_width)
           
#------------Init Directory Management-----------

    create_section("Set Root Directory", ic_window)
    
    #Current root directory
    cmds.rowLayout(numberOfColumns = 2, columnWidth2 = (column1_width, column2_width)) 
    cmds.text(label="Current Root Directory:")
    global root_text_field
    root_text_field = cmds.textField(placeholderText="Please, Select Directory...", width = 250)
    cmds.setParent('..')  # End the rowLayout
    
    #Set Root directory
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    cmds.text(label="Set Root Directory: ")
    cmds.button(label="Configure", command='open_file_dialog()', width = 100)
    cmds.setParent('..')  # End the rowLayout
   
#------------Init Save Assets----------------

    create_section("Save Assets", ic_window)
    
    #Current Save directory
    cmds.rowLayout(numberOfColumns=2, columnWidth2 = (column1_width, column2_width))
    cmds.text(label="Current Save Directory: ")  
    global save_text_field
    save_text_field = cmds.textField(placeholderText="Please, Select Directory...", width=250)   
    cmds.setParent('..')  # End the rowLayout

    #Save Directory Scroll List
    cmds.rowLayout(numberOfColumns=2, columnWidth2 = (column1_width, column2_width))
    global save_scroll_list
    save_scroll_list = cmds.textScrollList(
        isObscured = True,
        numberOfRows = 10,  
        allowMultiSelection = True, 
        width = window_width,
        height = 200,
        append = []  
    )
    cmds.setParent('..')
    
    #Refresh Asset List
    cmds.rowLayout(numberOfColumns=2, columnWidth2 = (column1_width, column2_width)) 
    cmds.text(label="Refresh Asset List:")
    cmds.button(label="Refresh List", command='addSaveListItems(save_dir)', width=100)
    cmds.setParent('..')  # End the rowLayout

    #Save Scene Type Menu
    cmds.rowLayout(numberOfColumns=2, columnWidth2 = (column1_width, column2_width)) 
    cmds.text(label="Select Scene Type:")
    global saveSceneTypeMenu, saveAssetSeqTypeMenu
    saveSceneTypeMenu = cmds.optionMenu(width=140)
    cmds.menuItem(label="Select Scene Type")
    [cmds.menuItem(label=str(scene_type)) for scene_type in scene_types]
    cmds.optionMenu(saveSceneTypeMenu, edit=True, changeCommand=lambda x: setSceneType(saveSceneTypeMenu, saveAssetSeqTypeMenu))
    cmds.setParent('..')  # End the rowLayout
    
    #Save Asset and Sequence Type Menu
    cmds.rowLayout(numberOfColumns=2, columnWidth2 = (column1_width, column2_width)) 
    cmds.text(label="Select Asset/Seq Type:")
    saveAssetSeqTypeMenu = cmds.optionMenu(width=140)    
    cmds.setParent('..')  # End the rowLayout
    
    #Save Diplayed Assets
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    cmds.text(label="Save displayed assets:")
    cmds.button(label="Save Assets", command='saveFiles()', width=100)
    cmds.setParent('..')  # End the rowLayout

#--------Init Publish Assets----------------

    create_section("Publish Assets", ic_window)

    #Current publish directory
    cmds.rowLayout(numberOfColumns=2, columnWidth2 = (column1_width, column2_width))
    cmds.text(label="Current Publish Directory:")   
    global publish_text_field
    publish_text_field = cmds.textField(placeholderText="Please, Select Directory...", width=250)   
    cmds.setParent('..')  # End the rowLayout
    
    #Publish directory scroll list
    cmds.rowLayout(numberOfColumns = 1, columnWidth1 = column1_width)
    global publish_scroll_list
    publish_scroll_list = cmds.textScrollList(
        numberOfRows = 10,  
        allowMultiSelection = True, 
        width = window_width,
        height = 200,
        append = []  
    )
    cmds.setParent('..')
    
    #Publish Refresh Asset List
    cmds.rowLayout(numberOfColumns=2, columnWidth2 = (column1_width, column2_width)) 
    cmds.text(label="Refresh Asset List:")
    cmds.button(label="Refresh List", command='addPublishListItems(publish_dir)', width=100)
    cmds.setParent('..')  # End the rowLayout
    
    #Publish Scene Type Menu
    cmds.rowLayout(numberOfColumns=2, columnWidth2 = (column1_width, column2_width)) 
    cmds.text(label="Select Scene Type:")
    global publishSceneTypeMenu
    publishSceneTypeMenu = cmds.optionMenu(width=140)
    cmds.menuItem(label="Select Scene Type")
    [cmds.menuItem(label=str(scene_type)) for scene_type in scene_types]
    cmds.optionMenu(publishSceneTypeMenu, edit=True, changeCommand=lambda x: setSceneType(publishSceneTypeMenu, publishAssetSeqTypeMenu))
    cmds.setParent('..')  # End the rowLayout
    
    #Publish Asset and Sequence Type Menu
    cmds.rowLayout(numberOfColumns=2, columnWidth2 = (column1_width, column2_width)) 
    cmds.text(label="Select Asset/Seq Type:")
    global publishAssetSeqTypeMenu
    publishAssetSeqTypeMenu = cmds.optionMenu(width=140)    
    cmds.setParent('..')  # End the rowLayout

    #Publish Displayed Assets
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    cmds.text(label="Publish Displayed Assets:")
    cmds.button(label="Publish Assets", command='publishFiles()', width=100)
    cmds.setParent('..')  # End the rowLayout

#--------------Init Logs-------------------- 
  
    create_section("Log Messages", ic_window)
    
    #Clean log messages
    cmds.rowLayout(numberOfColumns = 2, columnWidth2 = (column1_width, column2_width))
    cmds.text(label="Clean Log Messages:")
    cmds.button(label="Clean Log Messages", command=lambda x: clearTextScrollList(log_scroll_list))
    cmds.setParent('..')  # End the rowLayout
    
    #Log scroll list
    cmds.rowLayout(numberOfColumns = 1, columnWidth1 = column1_width)
    global log_scroll_list
    log_scroll_list = cmds.textScrollList(
        numberOfRows=10,  
        allowMultiSelection=True,  
        width=window_width,
        height=200,
        append=[]
    )    
    cmds.setParent('..')  # End the rowLayout
    
    #Reset UI
    cmds.separator(parent=ic_layout, style="single", annotation="buttons", height=15, width=window_width)       
    cmds.button(parent=ic_layout, label="Reset UI", command="reloadSavePublishTool()")     
    cmds.separator(parent=ic_layout, style="single", height=15, width = window_width)   
    cmds.showWindow(ic_window) 

#------------Window Reload------------------

def reloadSavePublishTool():  
    if cmds.window(toolName, exists = True):
        cmds.deleteUI(toolName)
    createUI()
#------------Show UI Window------------------
createUI()
# Script Name: Save/Publish Tool for Autodesk Maya
# Description: This tool provides a way for artists to save and publish their work in a way that
#automates the naming of the file and where the file/s are stored.

import os
import re
import maya.cmds as cmds
from functools import partial

scroll_list = None
naming_convention = r"^[A-Z]{1,3}_([A-Z]{1}[a-z]+)+$"
export_type = ""

#=======================================          
#----------------DEFS-------------------
#=======================================

def saveFiles():
    save_path = "/asset_wips/saved"
    asset_types_to_save = ["setPiece", "set", "prop", "character"]
    
    for asset_type in asset_types_to_save:
        asset_group = "|" + asset_type
        if cmds.objExists(asset_group):
            asset_roots = cmds.listRelatives(asset_group, children=True, fullPath=True)

            for asset in asset_roots:
                asset_name = asset.split("|")[-1]
                export_dir = "{0}/{1}/{2}".format(save_path,asset_type,asset_name)
                try:
                    os.makedirs(export_dir)
                except OSError:
                    print(export_dir + " already exists")
                file_name = "{0}_layout_v{1}.abc".format(asset_name, str(GetNextVersionNumber(asset_name, asset_type)).zfill(3))
                export_file = export_dir + "/" + file_name
                #SAVE .mb FILES HERE

def publishFiles(export_type):
    publish_path = "/asset_final/published"
    asset_types_to_publish = ["setPiece", "set", "layout", "animation"] 

    for asset_type in asset_types_to_publish:
        asset_group = "|" + asset_type
        if cmds.objExists(asset_group):
            asset_roots = cmds.listRelatives(asset_group, children=True, fullPath=True)

            #Alembic Export
            if (export_type == "alembic"):
                print("Exporting Alembic...")
                for asset in asset_roots:
                    asset_name = asset.split("|")[-1]
                    export_dir = "{0}/{1}/{2}".format(publish_path, asset_type, asset_name)
                    try:
                        os.makedirs(export_dir)
                    except OSError:
                        print(export_dir + " already exists")
                    file_name = "{0}_layout_v{1}.abc".format(asset_name, str(GetNextVersionNumber(publish_path, asset_name, asset_type)).zfill(3))
                    export_file = export_dir + "/" + file_name
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

            #FBX Export
            if (export_type == "fbx"):
                print("Exporting FBX...")
                for asset in asset_roots:
                    asset_name = asset.split("|")[-1]
                    export_dir = "{0}/{1}/{2}".format(publish_path, asset_type, asset_name)
                    try:
                        os.makedirs(export_dir)
                    except OSError:
                        print(export_dir + " already exists")
                    file_name = "{0}_layout_v{1}.abc".format(asset_name, str(GetNextVersionNumber(publish_path, asset_name, asset_type)).zfill(3))
                    export_file = export_dir + "/" + file_name           
                    cmds.file(export_file, force=True, options="v=0;", typ="FBX export", pr=True,  ea=True)


def GetLatestVersionNumber(path, asset_name, asset_type):
    dir = "{0}/{1}/{2}".format(path, asset_type,asset_name)
    found = False
    count = 1
    while found == False:
        if not os.path.isfile(dir + "/{0}_layout_v{1}.abc".format(asset_name, str(count).zfill(3))):
            found = True
            count = count - 1
        else:
            count = count + 1
    return count

def GetNextVersionNumber(path, asset_name, asset_type):
    return GetLatestVersionNumber(path, asset_name, asset_type) + 1

#=======================================          
#------------------UI-------------------
#=======================================
toolName = 'savePublishTool'
#----------------UI Defs----------------
def reset_text_fields_background_color():
    global text_fields
    print(text_fields)
    for text_field in text_fields:
        cmds.text(
            text_field, 
            edit=True, 
            backgroundColor=(0.2667, 0.2667, 0.2667)
            )

def create_section(section_title, parent):
    return cmds.frameLayout(label=section_title, collapsable=True, collapse=True, parent=parent, marginWidth=10, marginHeight=10)
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

    ic_window = cmds.window(
        toolName, 
        title = "Save Publish Tool for Autodesk Maya", 
        width = window_width, 
        height = window_height
        )
        
    ic_layout = cmds.columnLayout(adjustableColumn = True) 
#------------Init Tool Header--------------------
 
    cmds.separator(h=15, style="single", annotation="buttons", width = window_width)
    cmds.text(label='Asset Save/Publish Tool for Autodesk Maya', backgroundColor = color_grey, font="boldLabelFont", align='center', width = window_width)
    cmds.text(label='Saves, Publishes and automates file naming of assets', backgroundColor = color_grey, font="smallBoldLabelFont",  align='center', width = window_width)
    cmds.separator(h=15, style="single", annotation="buttons", width = window_width)
    
#------------Init Directory Management-----------
    create_section("Set Base Directory", ic_window)
    
    cmds.rowLayout(numberOfColumns = 2, columnWidth2 = (column1_width, column2_width)) 
    cmds.text(label="Current Directory:")
    cmds.text(label="'" + "NULL" + "'")
    cmds.setParent('..')  # End the rowLayout
    
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    cmds.text(label="Set Base Directory: ")
    cmds.button(label="Configure", command='placeholder()', width = 100)
    cmds.setParent('..')  # End the rowLayout
   
#------------Init Save Assets----------------

    create_section("Save Assets", ic_window)
    cmds.rowLayout(numberOfColumns = 1, columnWidth1 = column1_width)
    cmds.textScrollList(
        isObscured = True,
        numberOfRows = 10,  
        allowMultiSelection = True, 
        width = window_width,
        height = 300,
        append = []  
    )
    cmds.setParent('..')
    
    cmds.rowLayout(numberOfColumns = 2, columnWidth2 = (column1_width, column2_width)) 
    cmds.text(label="Refresh Asset List: ")
    cmds.button(label="Refresh List", command='placeholder()', width = 100)
    cmds.setParent('..')  # End the rowLayout
    
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    cmds.text(label="Save displayed assets:")
    cmds.button(label="Save Assets", command='placeholder()', width = 100)
    cmds.setParent('..')  # End the rowLayout

#--------Init Publish Assets----------------

    create_section("Publish Assets", ic_window)
    cmds.rowLayout(numberOfColumns = 1, columnWidth1 = column1_width)
    cmds.textScrollList(
        numberOfRows = 10,  
        allowMultiSelection = True, 
        width = window_width,
        height = 300,
        append = []  
    )
    cmds.setParent('..')
    
    cmds.rowLayout(numberOfColumns = 2, columnWidth2 = (column1_width, column2_width)) 
    cmds.text(label="Refresh Asset List: ")
    cmds.button(label="Refresh List", command='placeholder()', width = 100)
    cmds.setParent('..')  # End the rowLayout

    cmds.rowLayout(numberOfColumns=3, columnWidth3=(column1_width, column2_width, column3_width))
    cmds.text(label="Publish Displayed Assets:")
    cmds.button(label="Publish Assets", command='placeholder()', width = 100)
    cmds.setParent('..')  # End the rowLayout

#--------------Init Logs-------------------- 
  
    create_section("Log Messages", ic_window)
    cmds.rowLayout(numberOfColumns = 2, columnWidth2 = (column1_width, column2_width))
    title_label = cmds.text(label="Log Messages")
    cmds.button(label="Clean Log Messages", command='reset_text_fields_background_color()')
    cmds.setParent('..')  # End the rowLayout
    
    cmds.rowLayout(numberOfColumns = 1, columnWidth1 = column1_width)
    global scroll_list
    scroll_list = cmds.textScrollList(
        numberOfRows=10,  
        allowMultiSelection=True,  
        width=window_width,
        height=300,
        append=[]
    )    
    cmds.setParent('..')  # End the rowLayout
    cmds.showWindow(ic_window)
#------------Window Reload------------------

def reloadSavePublishTool():  
    if cmds.window(toolName, exists = True):
        cmds.deleteUI(toolName)
    createUI()
#------------Show UI Window------------------
createUI()
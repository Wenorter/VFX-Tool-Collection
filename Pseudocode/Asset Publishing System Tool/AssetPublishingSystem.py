#Pseudocode for Asset Saving/Publishing Tool

import maya.cmds as cmds

def savePublishTool():
    
    if cmds.window('savePublishTool', exists = True):
        cmds.deleteUI('savePublishTool')
        
    cmds.window('savePublishTool', resizeToFitChildren=True)
    cmds.window('savePublishTool', widthHeight=(200, 450))

    cmds.columnLayout(
        backgroundColor = [0.1, 0.1, 0.1], #black skin
        #columnAlign ="center", 
        #columnOffset =["both", 5],
        rowSpacing = 10
        ) 
    

def saveAssets():
    start = 0
    end = 120
    root = "-root pSphere1 -root pCube1" #will use command for extracting model, layout, animation, lighting
    path_name = "C:/saveFilePath/"
    file_name = "alembicTest"
    extension = ".abc"  

    command = "-frameRange " + start + " " + end +" -uvWrite -worldSpace " + root + " -file " + path_name + file_name
    cmds.AbcExport (j = command)

def publishAssets():
    start = 0
    end = 120
    root = "-root pSphere1 -root pCube1"
    path_name[] = ["C:/saveFilePath01/", "C:/saveFilePath02/"] #paths are going to be saved in a collection
    file_name = "alembicTest"
    extension = ".abc" #will have between Alembic/FBX depending select box value

for x in xrange(1,10):
  
    #using for loop we are going to extract files to different directories
    command = "-frameRange " + start + " " + end +" -uvWrite -worldSpace " + root + " -file " + path_name[x]  file_name
    if extension == ".abc":
        print("exporting alembix file")
        cmds.AbcExport (j = command)  
    if extension == ".fbx":
        print("exporting FBX file")
        cmds.FbxExport (j = command)  

# ============================================================
# UI
# =============================================================

cmds.separator(h=2, backgroundColor = [0.5, 0.5, 0.5], style="single", annotation="buttons", width=cmds.getAttr('defaultResolution.width'))
cmds.text(label='Save/Publish Tool', font="boldLabelFont", align='center', width=cmds.getAttr('defaultResolution.width'))
cmds.separator(h=2, backgroundColor = [0.5, 0.5, 0.5], style="single", annotation="buttons", width=cmds.getAttr('defaultResolution.width'))

cmds.button(label = 'Save', command = 'saveAssets()')
cmds.button(label = 'Export', command = 'exportAnim()')

cmds.showWindow('savePublishTool')

savePublishTool()
from core.MayaWidget import MayaWidget # This imports the MayaWidget class from the MayaWidget module
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel, QColorDialog #This imports QtWidget classes from PySide6.QtWidgets these are used to build the ui layout, buttons and text inputs
import maya.cmds as mc #This imports mayas command module (maya.cmds) and gives it the name mc for an easier access when making commands
from maya.OpenMaya import MVector #This imports the MVector class form Mayas OpenMaya API

import importlib #This imports pythons importlib This helps you reload modules without have to reopen maya or python
import core.MayaUtilities # This imports mayautilities
importlib.reload(core.MayaUtilities) #This makes python reload to pick up any recently added code
from core.MayaUtilities import CreateCircleControllerForJnt, CreateBoxControllerForJnt, CreatePlusController, ConfigureCtrlForJnt, GetObjectPositionAsMVec #This imports specific fuctions from mayautilities (such as the ones listed)

class LimbRigger: # This is a class holding all the fuctions needed to make the rig in maya 
     def __init__(self): # This defines the constructor method that starts once the class is initiated
        self.nameBase = "" # This makes a variable to store a name base 
        self.controllerSize = 10 # This sets the default size for the controller to 10
        self.blendControllerSize = 4 # This sets the default size for the blend controller to 4
        self.controlColorRGB = [0,0,0] # This sets the default color controller using RGB vaules

     def SetNameBase(self, newNameBase): # This defines the method "SetNameBase" then uses the new value "newnamebase" to update the name base
        self.nameBase = newNameBase # This gives the value passed in newNameBase to the objects in nameBase
        print(f"name base is set to: {self.nameBase}") #This prints a text message showing the updated nameBase vaule to show if its working or not

     def SetControllerSize(self, newControllerSize): # This defines a method that updates the controller size by using the new value
        self.controllerSize = newControllerSize # This sets the object controllerSize to the new value passed 

     def SetBlendControllerSize(self, newBlendControllerSize): #This defines a method that updates the blend controller size
         self.blendControllerSize = newBlendControllerSize # This gives a new vaule to the blendControllerSize with the object

     def RigLimb(self): #This defines a method call RigLimb
        print("Start rigging!!") # This prints out a text saying "start rigging!!" we used this as a test code 
        rootJnt, midJnt, endJnt = mc.ls(sl=True) # This gets the current object thats selected in maya to assigns them as (rootJnt, midJnt, endJnt)
        print(f"found root {rootJnt}, mid: {midJnt} and end: {endJnt}") #This prints out the selected joints so you know it was properly picked

        rootCtrl, rootCtrlGrp = CreateCircleControllerForJnt(rootJnt, "fk_" + self.nameBase,self.controllerSize) # This makes a circle control for the root jnt names it "fk_ + namebase" and sets its size using the controllersize
        midCtrl, midCtrlGrp = CreateCircleControllerForJnt (midJnt, "fk_" + self.nameBase, self.controllerSize) # This makes a circle control for the mid jnt names it "fk_ + namebase" and sets its size using the controllersize
        endCtrl, endCtrlGrp = CreateCircleControllerForJnt (endJnt, "fk_" + self.nameBase, self.controllerSize) # This makes a circle control for the end jnt names it "fk_ + namebase" and sets its size using the controllersize

        #These make the right hierachy by parenting in the right order 
        mc.parent(endCtrlGrp, midCtrl) #This parents the end controler group under the middle controler group
        mc.parent(midCtrlGrp, rootCtrl) #This parents the mid controler group under the root controler group 

        endIkCtrl , endIkCtrlGrp = CreateBoxControllerForJnt(endJnt, "ik_" + self.nameBase, self.controllerSize) # This makes an ik contoler in a box shape for the endjnt
      
        IkFkBlendCtrlPrefix = self.nameBase + "_ikfkBlend" # This makes a name string for the IK and FK blend controler
        IkFkBlendController = CreatePlusController(IkFkBlendCtrlPrefix, self.blendControllerSize) # This makes a plus-shape controller for blending ik and fk by using the blend size vaule 
        IkFkBlendController, IkFkBlendControllerGrp = ConfigureCtrlForJnt(rootJnt, IkFkBlendController, False) # This configures the blend controller relative to the rootjnt

        ikfkBlendAttrName = "ikfkBlend" # This is 
        mc.addAttr(IkFkBlendController, ln=ikfkBlendAttrName, min=0, max=1, k=True) # This is 

        ikHandleName = "ikHandle_" + self.nameBase # This is 
        mc.ikHandle(n=ikHandleName, sj = rootJnt, ee=endJnt, sol="ikRPsolver") # This is 

        rootJntLoc = GetObjectPositionAsMVec(rootJnt) # This is 
        endJntLoc = GetObjectPositionAsMVec(endJnt) # This is 

        poleVectorVals =mc.getAttr(f"{ikHandleName}.poleVector")[0] # This is 
        poleVecDir = MVector(poleVectorVals[0], poleVectorVals[1], poleVectorVals[2]) # This is 
        poleVecDir.normalize() # This is 

        rootToEndVec = endJntLoc - rootJntLoc # This is 
        rootToEndDist = rootToEndVec.length() # This is 

        poleVectorCtrlLoc = rootJntLoc + rootToEndVec/2.0 + poleVecDir * rootToEndDist # This is 

        poleVectorCtrlName = "ac_ik_" + self.nameBase + "poleVector" # This is 
        mc.spaceLocator(n=poleVectorCtrlName) # This is 

        poleVectorCtrlGrpName = poleVectorCtrlName + "_grp" # This is 
        mc.group(poleVectorCtrlName, n = poleVectorCtrlGrpName) # This is 

        mc.setAttr(f"{poleVectorCtrlGrpName}.translate", poleVectorCtrlLoc.x, poleVectorCtrlLoc.y, poleVectorCtrlLoc.z, type="double3") # This is 
        mc.poleVectorConstraint(poleVectorCtrlName,ikHandleName) # This is 

        mc.parent(ikHandleName, endIkCtrl) # This is 
        mc.setAttr(f"{ikHandleName}.v", 0) # This is 

        mc.connectAttr(f"{IkFkBlendController}.{ikfkBlendAttrName}", f"{ikHandleName}.ikBlend") # This is 
        mc.connectAttr(f"{IkFkBlendController}.{ikfkBlendAttrName}", f"{endIkCtrl}.v") # This is 
        mc.connectAttr(f"{IkFkBlendController}.{ikfkBlendAttrName}", f"{poleVectorCtrlGrpName}.v") # This is 

        reverseNodeName = f"{self.nameBase}_reverse" # This is 
        mc.createNode("reverse", n=reverseNodeName) # This is 

        mc.connectAttr(f"{IkFkBlendController}.{ikfkBlendAttrName}",f"{reverseNodeName}.inputX") # This is 
        mc.connectAttr(f"{reverseNodeName}.outputX", f"{rootCtrlGrp}.v") # This is 

        orientConstaint = None # This is 
        wristConnections = mc.listConnections(endJnt) # This is 
        for connection in wristConnections: # This is 
            if mc.objectType(connection) == "orientConstraint": # This is 
                orientConstaint = connection # This is 
                break # This is 

        mc.connectAttr(f"{IkFkBlendController}.{ikfkBlendAttrName}", f"{orientConstaint}.{endIkCtrl}W1") # This is 
        mc.connectAttr(f"{reverseNodeName}.outputX", f"{orientConstaint}.{endCtrl}W0") # This is 

        topGrpName = f"{self.nameBase}_rig_grp" # This is 
        mc.group(n=topGrpName, empty=True) # This is 
 
        mc.parent(rootCtrlGrp, topGrpName) # This is 
        mc.parent(IkFkBlendControllerGrp, topGrpName) # This is 
        mc.parent(endIkCtrlGrp, topGrpName) # This is 
        mc.parent(poleVectorCtrlGrpName, topGrpName) # This is 

        mc.setAttr(f"{topGrpName}.overrideEnabled", 1) #Overriding the dsipay attributes 
        mc.setAttr(f"{topGrpName}.overrideRGBColors",1) # This Switches from index-based colors to RGB color mode

        r, g, b = self.controlColorRGB #This gets the RGB values selected by the user 
        mc.setAttr(f"{topGrpName}.overrideColorRGB", r, g, b) #Applies the picked RGB color to the controls

        self.ApplyColor(topGrpName) #This is just calling for the helper function to finsh the color setting


class LimbRiggerWidget(MayaWidget): # This is a class holding all the fuctions needed to make the viusal UI in maya
    def __init__(self): # This is 
        super().__init__() # This is 
        self.setWindowTitle("Limb Rigger") # This is the name 
        self.rigger = LimbRigger() # This is creating an instance of the LimbRigger class then stores it
        self.masterLayout = QVBoxLayout() # This is creating a vertical placement for the UI widget
        self.setLayout(self.masterLayout) # This applies the layout to this widget

        self.masterLayout.addWidget(QLabel("Select the 3 joints of the limb, from base to end, and then:")) # This adds a label "Select the 3 joints of the limb, from base to end, and then:" to the UI layout

        self.infoLayout =QHBoxLayout() #This is making a horizontal layout and assigns it to self.infoLayout
        self.masterLayout.addLayout(self.infoLayout) #  This is adding the horizontal layout into the main (vertical) layout
        self.infoLayout.addWidget(QLabel("Name Base:")) # This adds a label widget with the text "Name Base:"

        self.nameBaseLineEdit = QLineEdit() # This makes a text input box and stores it in (self.nameBaseLineEdit)
        self.infoLayout.addWidget(self.nameBaseLineEdit) # This adds the text input box into the horizontal layout so it shows in the UI along with the other widgets

        self.setNameBaseBtn = QPushButton("Set Name Base") #This is making a button with the lable "set name Base"
        self.setNameBaseBtn.clicked.connect(self.setNameBaseBtnClicked) #This connects the button to signal the function (setNameBaseBtnClicked)
        self.infoLayout.addWidget(self.setNameBaseBtn) # This adds the button to the ui layout 

        self.colorBtn = QPushButton() # This is making the button 
        self.colorBtn.setFixedSize(300,30) # This is setting the size of the button (width/ height)
        self.colorBtn.setStyleSheet("background-color: #ffffff;") # This is setting the initial background color for the buttton 
        self.masterLayout.addWidget(self.colorBtn) # This is setting the location of the button in the main layout
        self.colorBtn.clicked.connect(self.ColorPicker) # This connects the button click event to the ColorPicker fuction 
        
        self.rigLimbBtn = QPushButton("Rig Limb") # This makes a button with the text "Rig Limb"
        self.rigLimbBtn.clicked.connect(self.RigLimbBtnClicked) # This runs the fuction (RigLimbBtnClicked) once the button has been clicked 
        self.masterLayout.addWidget(self.rigLimbBtn) # This puts the button on the main layout 

    def setNameBaseBtnClicked(self): # This defines the function that runs when the "Set Name Base" button is clicked
        self.rigger.SetNameBase(self.nameBaseLineEdit.text()) # This sts the rig naming prefix using the text the user typed out in the UI space

    def RigLimbBtnClicked(self): # This defines the fuction that runs when the "Rig Limb" button is clicked
        self.rigger.RigLimb() # This runs the rigging fuction

    def GetWidgetHash(self): # This is the hash number that stop the window fro duplcating 
        return "403b60dd84c346f44dba8246a8d5d18ea6ee9aa1bfc9b1549fdcc4558689d3f4" # This is the unqiue hash number 
    
    def ColorPicker(self): # This opens the ColorPicker dialog
        color = QColorDialog.getColor(parent=self) #This displays a color picker window and returns to the chosen color

        if color.isValid(): # This ensures the user picked a valid color
            r = color.red() / 255.0  
            g = color.green() / 255.0
            b = color.blue() / 255.0 #This is the RGB values that maya requires 
            
            self.rigger.controlColorRGB = [r,g,b] #This Stores the chosen color for use in Maya

            self.colorBtn.setStyleSheet(f"background-color: rgb({color.red()},{color.green()},{color.blue()});") #This updates the widgets background color to match the chosen color 
            
def Run(): # This runs the code
        limbRiggerWidget = LimbRiggerWidget() # this creates a new instance of the LimnRiggerWidget class and places it in the LimbRiggerWidget
        limbRiggerWidget.show() # This opens the limbRiggerWidget window 

Run() # This runs the code
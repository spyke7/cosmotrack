from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task import Task
import math
from cosmotrack.renderer.naturalobjects import NaturalObject

def itemSel(arg):
    output = "Item Selected is: " + arg
    textObject.setText(output)

class CosmotrackApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.setBackgroundColor(0,0,0,1)
        
        props = WindowProperties()
        props.setTitle("Cosmotrack")
        
        props.setSize(1480, 900) 
        props.setOrigin(100, 100)
        props.setFixedSize(True) 
        
        self.naturalObjectCreator = NaturalObject()
        
        self.sidebarCollapsed = False
        self.selectedNaturalObject = "Earth"
        self.naturalDropdownOpen = False
        self.naturalOptions = ["Earth", "Moon", "Mars"]
        self.artificialDropdownOpen=False
        self.artificialOptions = ["Satellites", "Stations", "None"]
        self.selectedArtificialType = None  
        self.searchText = ""
        self.currentPage = 0
        
        self.win.requestProperties(props)
        
        self.setup3DScene()
        
        self.sideBarHandler()
    
    
    # the whole 3D setup
    def setup3DScene(self):
        self.disableMouse()
        
        self.camera.setPos(0, -40, 0) 
        self.camera.lookAt(0, 0, 0)
        
        self.setupLighting()
        
        # self.createEarth()
        self.earth = self.naturalObjectCreator.createEarth(self.render, self.loader)
        
        self.taskMgr.add(self.rotateEarthTask, "rotateEarth")
    
    def setupLighting(self):
        ambientLight = AmbientLight("ambient")
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNP = self.render.attachNewNode(ambientLight)
        self.render.setLight(ambientLightNP)
        
        directionalLight = DirectionalLight("directional")
        directionalLight.setColor((0.8, 0.8, 0.8, 1))
        directionalLightNP = self.render.attachNewNode(directionalLight)
        directionalLightNP.setHpr(45, -45, 0)  
        self.render.setLight(directionalLightNP)
        
    def rotateEarthTask(self, task):
        angleDegrees = task.time * (10)
        
        self.earth.setHpr(angleDegrees, 0, 0)
        
        return Task.cont
    
    # functions for handling elements of the main sidebar
    def sideBarHandler(self):
        self.sidebar = DirectFrame(frameColor=(0.1, 0.1, 0.1, 0.85),
                                   frameSize=(-0.25, 0.5, -1, 1),
                                   pos=(-1.40, 0, 0))
        self.sidebar.setTransparency(TransparencyAttrib.MAlpha)
        self.sidebar.setClipPlaneOff()
        
        
        self.collapseBtn= DirectButton(
            image="../assets/left-chevron.png",
            scale=0.03,
            # pos=(0,0,0),
            frameSize=(-1.2, 1.2, -1.2, 1.2),
            pos=(-1.55, 0, 0.9),
            command=self.toggleSidebarHandler,
            # relief=DGG.FLAT
        )
        
        self.createNaturalObjectsSection()
        
        self.createArtificialObjectsSection()
        
        self.createNaturalDropdown()
        
        self.createArtificialDropdown()
        
    def toggleSidebarHandler(self):
        self.sidebarCollapsed = not self.sidebarCollapsed
        
        if self.sidebarCollapsed:
            self.sidebar.setPos(-2.60, 0, 0) 
            self.collapseBtn['image'] = "../assets/right-chevron.png"
            
        else:
            self.sidebar.setPos(-1.40, 0, 0)
            self.collapseBtn['image'] = "../assets/left-chevron.png"
      
    # for showing natural objects       
    def createNaturalObjectsSection(self):
        naturalLabel = DirectLabel(
            text="Natural Objects",
            scale=0.045,
            pos=(-0.20, 0, 0.75),
            text_fg=(0.8, 0.8, 0.8, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            parent=self.sidebar
        )
        
        self.naturalObjectBtn = DirectButton(
            text="Earth ", 
            scale=0.045,
            pos=(-0.16, 0, 0.68),
            frameSize=(-0.8, 3.2, -0.5, 1),
            frameColor=(0.2, 0.2, 0.2, 0.9),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft,
            relief=DGG.FLAT,
            command=self.toggleNaturalDropdown,
            parent=self.sidebar
            
        )
    
    def createNaturalDropdown(self):
        self.naturalDropdownFrame = DirectFrame(
            frameColor=(0.15, 0.15, 0.15, 0.95),
            frameSize=(-0.16, 0.16, -0.15, 0),
            pos=(-0.16, 0, 0.64),  
            parent=self.sidebar
        )
        self.naturalDropdownFrame.hide()
        
        self.naturalDropdownButtons = []
        yOffset = -0.025
        
        for option in self.naturalOptions:
            btn = DirectButton(
                text=option,
                scale=0.04,
                pos=(0, 0, yOffset),
                frameSize=(-1, 3.8, -0.8, 1.1),
                frameColor=(0.18, 0.18, 0.18, 1),
                text_fg=(0.9, 0.9, 0.9, 1),
                text_align=TextNode.ALeft,
                relief=DGG.FLAT,
                command=self.selectNaturalObject,
                extraArgs=[option],
                parent=self.naturalDropdownFrame
            )
            
            self.naturalDropdownButtons.append(btn)
            yOffset -= 0.05 
        
        dropdownHeight = len(self.naturalOptions) * 0.05 + 0.01
        self.naturalDropdownFrame['frameSize'] = (0, 0.16, -dropdownHeight, 0)
        
        
    def toggleNaturalDropdown(self):
        self.naturalDropdownOpen = not self.naturalDropdownOpen
        
        if self.naturalDropdownOpen:
            self.naturalDropdownFrame.show()
            self.naturalObjectBtn['text'] = f"{self.selectedNaturalObject}" 
        else:
            self.naturalDropdownFrame.hide()
            self.naturalObjectBtn['text'] = f"{self.selectedNaturalObject}" 
            
    def selectNaturalObject(self, selectedObject):
        self.selectedNaturalObject = selectedObject
        
        self.naturalObjectBtn['text'] = f"{selectedObject}"
        
        self.naturalDropdownOpen = False
        self.naturalDropdownFrame.hide()
        
        
    # for handling artificial objects
    def createArtificialObjectsSection(self):
        artificalLabel = DirectLabel(
            text="Artifical Objects",
            scale=0.045,
            pos=(-0.19, 0, 0.55),
            text_fg=(0.8, 0.8, 0.8, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            parent=self.sidebar
        )
        
        self.artificialObjectBtn = DirectButton(
            text="None", 
            scale=0.045,
            pos=(-0.17, 0, 0.48),
            frameSize=(-0.7, 4.6, -0.5, 1),
            frameColor=(0.2, 0.2, 0.2, 0.9),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft,
            relief=DGG.FLAT,
            command=self.toggleArtificialDropdown,
            parent=self.sidebar
            
        )
    
    def toggleArtificialDropdown(self):
        self.artificialDropdownOpen = not self.artificialDropdownOpen
        
        if self.artificialDropdownOpen:
            self.artificialDropdownFrame.show()
            self.artificialObjectBtn['text'] = f"{self.selectedArtificialType}" 
        else:
            self.artificialDropdownFrame.hide()
            self.artificialObjectBtn['text'] = f"{self.selectedArtificialType}" 
    
    def createArtificialDropdown(self):
        self.artificialDropdownFrame = DirectFrame(
            frameColor=(0.15, 0.15, 0.15, 0.95),
            frameSize=(-0.19, 0.16, -0.15, 0),
            pos=(-0.17, 0, 0.44),  
            parent=self.sidebar
        )
        self.artificialDropdownFrame.hide()
        
        self.artificialDropdownButtons = []
        yOffset = -0.025
        
        for option in self.artificialOptions:
            btn = DirectButton(
                text=option,
                scale=0.04,
                pos=(0, 0, yOffset),
                frameSize=(-1, 4.4, -0.8, 1.1),
                frameColor=(0.18, 0.18, 0.18, 1),
                text_fg=(0.9, 0.9, 0.9, 1),
                text_align=TextNode.ALeft,
                relief=DGG.FLAT,
                command=self.selectArtificialObject,
                extraArgs=[option],
                parent=self.artificialDropdownFrame 
            )
            
            self.artificialDropdownButtons.append(btn)
            yOffset -= 0.05 
        
        dropdownHeight = len(self.artificialOptions) * 0.05 + 0.01
        self.artificialDropdownFrame['frameSize'] = (0, 0.16, -dropdownHeight, 0)
    
    def selectArtificialObject(self, selectedObject):
        self.selectedArtificialType = selectedObject
        
        self.artificialObjectBtn['text'] = f"{selectedObject}"
        
        self.artificialDropdownOpen = False
        self.artificialDropdownFrame.hide()
    
    # def selectArtificialType(self, objType):
    #     """Handle artificial object type selection"""
    #     self.selectedArtificialType = objType
    #     print(f"Selected type: {objType}")
        
    #     # Update button colors
    #     if objType == "Satellites":
    #         self.satellitesBtn['frameColor'] = (0.2, 0.4, 0.8, 0.9)
    #         self.stationsBtn['frameColor'] = (0.2, 0.2, 0.2, 0.9)
    #     else:
    #         self.stationsBtn['frameColor'] = (0.2, 0.4, 0.8, 0.9)
    #         self.satellitesBtn['frameColor'] = (0.2, 0.2, 0.2, 0.9)
from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task import Task
from cosmotrack.data.satellite_tracker import SatelliteTracker, latLonAltTo3D
from cosmotrack.renderer.artificialobjects import ArtificialObject
import math
from cosmotrack.renderer.naturalobjects import NaturalObject

def itemSel(arg):
    output = "Item Selected is: " + arg
    textObject.setText(output)

class CosmotrackApp(ShowBase):
    def __init__(self, satelliteData, stationsData):
        super().__init__()
        self.setBackgroundColor(0,0,0,1)
        
        props = WindowProperties()
        props.setTitle("Cosmotrack")
        
        props.setSize(1480, 900) 
        props.setOrigin(100, 100)
        props.setFixedSize(True) 
        
        self.lastMousePos = None
        self.rotationSpeed = 100

        self.naturalObjectCreator = NaturalObject()
        self.artificialObjectCreator = ArtificialObject()
        
        self.sidebarCollapsed = False
        self.selectedNaturalObject = "Earth"
        self.naturalDropdownOpen = False
        self.naturalOptions = ["Earth", "Moon", "Mars"]
        self.artificialDropdownOpen=False
        self.artificialOptions = ["Satellites", "Stations", "None"]
        self.selectedArtificialType = "None"  
        
        
        self.satellitesData = satelliteData[:30] 
        self.stationsData = stationsData
        
        self.stationsList = [sat[0] for sat in self.stationsData]
        self.satellitesList = [sat[0] for sat in self.satellitesData]
        
        self.satelliteTracker = SatelliteTracker()  
        self.satelliteDots = {}  
        self.activeSatellites = [] 
        self.detailsPanelCreated = False
        
        self.totalCount = 0
        self.showObjectList = False
        # self.searchText = ""
        self.currentObjectList = []
        self.itemsPerPage = 10
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
        
        # creating earth
        self.earth = self.naturalObjectCreator.createEarth(self.render, self.loader)
        self.earth.setH(180)
        self.taskMgr.add(self.rotateEarthTask, "rotateEarth")
        
        # attaching earth to the main scene
        self.sceneRoot = self.render.attachNewNode("sceneRoot")
        self.earth.reparentTo(self.sceneRoot)
        self.dragging = False
        self.prevMouseX = 0
        self.prevMouseY = 0

        self.accept("mouse1", self.startDrag)
        self.accept("mouse1-up", self.stopDrag)

        self.taskMgr.add(self.dragRotateTask, "DragRotateTask")
    
    def startDrag(self):
        if self.win.getPointer(0):
            p = self.win.getPointer(0)
            self.prevMouseX = p.getX()
            self.prevMouseY = p.getY()
            self.dragging = True

    def stopDrag(self):
        self.dragging = False

    def dragRotateTask(self, task):
        if not self.dragging:
            return Task.cont

        if not self.win.getPointer(0):
            return Task.cont

        p = self.win.getPointer(0)
        x = p.getX()
        y = p.getY()

        dx = x - self.prevMouseX
        dy = y - self.prevMouseY

        self.prevMouseX = x
        self.prevMouseY = y

        # Rotate whole Earth + satellites
        self.sceneRoot.setH(self.sceneRoot.getH() - dx * 0.3)
        self.sceneRoot.setP(self.sceneRoot.getP() - dy * 0.3)

        return Task.cont

    
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
        totalTime = 86400
        timeElapsed=task.time
        
        rotationFraction = (timeElapsed / totalTime) % 1.0
        
        self.earth.setTexOffset(TextureStage.getDefault(), rotationFraction, 0)
        
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
            frameSize=(-1.2, 1.2, -1.2, 1.2),
            pos=(-1.55, 0, 0.9),
            command=self.toggleSidebarHandler,
        )
        
        self.createNaturalObjectsSection()
        
        self.createArtificialObjectsSection()
        
        self.createNaturalDropdown()
        
        self.createArtificialDropdown()        
        
        self.createObjectListSelection()
        self.objectListSection.hide()
        
        
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
        
        self.artificialDropdownFrame.hide()
        
        if selectedObject == "Satellites":
            self.currentObjectList = self.satellitesList
            self.showObjectList = True
            self.totalCount = len(self.currentObjectList)
            self.objectListSection.show()
            self.objectCountLabel['text'] = f"Total {selectedObject}: {self.totalCount}"
            self.updateObjectList()   
            
            self.initializeSatellites()
            
        elif selectedObject=="Stations":
            self.currentObjectList = self.stationsList
            self.showObjectList = True
            self.totalCount = len(self.currentObjectList)
            
            self.objectListSection.show()
            self.objectCountLabel['text'] = f"Total {selectedObject}: {self.totalCount}"
            self.updateObjectList()   
            
            self.initializeSatellites()
        
        elif selectedObject=="None":
            if (self.showObjectList):
                self.showObjectList = False
                self.objectListSection.hide()
            else:
                self.showObjectList = False

            for name, dot in self.satelliteDots.items():
                dot.removeNode()
            self.satelliteDots.clear()
            self.activeSatellites.clear()
        
        self.artificialDropdownOpen = False
        self.artificialDropdownFrame.hide()
    
    def initializeSatellites(self):
        for name, dot in self.satelliteDots.items():
            dot.removeNode()
        self.satelliteDots.clear()
        self.satelliteTracker.satellites.clear()
        
        if self.selectedArtificialType == "Satellites":
            data = self.satellitesData
        elif self.selectedArtificialType == "Stations":
            data = self.stationsData
        else:
            return
        
        print(f"Initializing {len(data)} {self.selectedArtificialType}...")
        
        for name, line1, line2 in data:
            self.satelliteTracker.addSatellite(name, line1, line2)
            
            dot = self.artificialObjectCreator.createSatelliteDot(
                radius=0.05,  
                color=(1, 0, 0, 1) 
            )
            dot.reparentTo(self.sceneRoot)  
            
            self.satelliteDots[name] = dot
            self.activeSatellites.append(name)
        
        print(f"Created {len(self.satelliteDots)} satellite dots")
        
        if not hasattr(self, 'satelliteUpdateTaskStarted'):
            self.taskMgr.add(self.updateSatellitesTask, "updateSatellites")
            self.satelliteUpdateTaskStarted = True
            
    def updateSatellitesTask(self, task):
        if not self.activeSatellites:
            return Task.cont  
        
        positions = self.satelliteTracker.getAllPositions()
        
        for name in self.activeSatellites:
            if name in positions and name in self.satelliteDots:
                lat, lon, alt = positions[name]
                
                x, y, z = latLonAltTo3D(lat, lon, alt, earthRadius=6.378)
                
                self.satelliteDots[name].setPos(x, y, z)
        
        return Task.cont
    
    def createObjectListSelection(self):
        self.currentPage = 0 
        # totalCount = len(self.currentObjectList)
        # self.totalCount=32
        self.objectListSection = DirectFrame(
            frameColor=(0.12, 0.12, 0.12, 0.95),
            frameSize=(-0.22, 0.40, -1, 0.08),
            pos=(0.015, 0, 0.2),
            parent=self.sidebar
        )
        
        self.objectCountLabel = DirectLabel(
            text=f"Total {self.selectedArtificialType}: {self.totalCount}",
            scale=0.035,
            pos=(-0.07, 0, 0.04),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            parent=self.objectListSection
        )
        
        self.objectScrollFrame = DirectScrolledFrame(
            frameSize=(-0.22, 0.40, -0.85, 0.16),
            canvasSize=(-0.18, 0.18, -1.5, 0),
            frameColor=(0.15, 0.15, 0.15, 0.9),
            scrollBarWidth=0.015,
            verticalScroll_frameColor=(0.25, 0.25, 0.25, 0.8),
            verticalScroll_thumb_frameColor=(0.4, 0.4, 0.4, 0.9),
            pos=(0, 0, -0.15),
            parent=self.objectListSection
        )
        
        paginationFrame = DirectFrame(
            frameColor=(0, 0, 0, 0),
            frameSize=(-0.20, 0.20, -0.04, 0.04),
            pos=(0.08, 0, -0.95),
            parent=self.objectListSection
        )
        
        self.prevPageBtn = DirectButton(
            image="../assets/left-chevron.png",
            scale=0.03,
            pos=(-0.12, 0, 0),
            frameSize=(-1.2, 1.2, -0.8, 0.8),
            frameColor=(0.2, 0.2, 0.2, 0.9),
            command=self.previousPage,
            parent=paginationFrame,
        )
        
        self.pageIndicatorLabel = DirectLabel(
            text="",
            scale=0.03,
            pos=(0, 0, 0),
            text_fg=(0.8, 0.8, 0.8, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            parent=paginationFrame
        )
        
        self.nextPageBtn = DirectButton(
            image="../assets/right-chevron.png",
            scale=0.03,
            pos=(0.12, 0, 0),
            frameSize=(-1.2, 1.2, -0.8, 0.8),
            frameColor=(0.2, 0.2, 0.2, 0.9),
            command=self.nextPage,
            parent=paginationFrame,
        )
                
    def updateObjectList(self):
        for child in self.objectScrollFrame.getCanvas().getChildren():
            child.removeNode()
        
        self.totalCount = len(self.currentObjectList)
        # Calculate pagination
        totalItems = len(self.currentObjectList)
        totalPages = (totalItems + self.itemsPerPage - 1) // self.itemsPerPage
        startIdx = self.currentPage * self.itemsPerPage
        endIdx = min(startIdx + self.itemsPerPage, totalItems)
        
        pageItems = self.currentObjectList[startIdx:endIdx]
        
        # Create item cards
        yPos = -0.05
        for i, objectName in enumerate(pageItems):
            itemNum = startIdx + i + 1
            self.createObjectItem(objectName, itemNum, yPos)
            yPos -= 0.13
        
        # Update canvas size
        canvasHeight = max(len(pageItems) * 0.12 + 0.1, 0.8)
        self.objectScrollFrame['canvasSize'] = (-0.18, 0.18, -canvasHeight, 0)
        
        # Update page indicator
        if totalPages > 0:
            self.pageIndicatorLabel['text'] = f"Page {self.currentPage + 1}/{totalPages}"
        else:
            self.pageIndicatorLabel['text'] = "No items"
        
        # Enable/disable pagination buttons
        if self.currentPage <= 0:
            self.prevPageBtn['state'] = DGG.DISABLED
            self.prevPageBtn['text_fg'] = (0.4, 0.4, 0.4, 1)
        else:
            self.prevPageBtn['state'] = DGG.NORMAL
            self.prevPageBtn['text_fg'] = (1, 1, 1, 1)
        
        if self.currentPage >= totalPages - 1:
            self.nextPageBtn['state'] = DGG.DISABLED
            self.nextPageBtn['text_fg'] = (0.4, 0.4, 0.4, 1)
        else:
            self.nextPageBtn['state'] = DGG.NORMAL
            self.nextPageBtn['text_fg'] = (1, 1, 1, 1)

    def createObjectItem(self, name, number, yPos):        
        itemCard = DirectButton(
            frameSize=(-0.17, 0.42, -0.058, 0.055),
            frameColor=(0.18, 0.18, 0.18, 0.9),
            pos=(0, 0, yPos),
            command=self.selectObjectItem,
            extraArgs=[name],
            parent=self.objectScrollFrame.getCanvas(),
            relief=DGG.FLAT
        )
        
        numLabel = DirectLabel(
            text=f"{number}.",
            scale=0.03,
            pos=(-0.15, 0, 0),
            text_fg=(0.6, 0.6, 0.6, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            parent=itemCard
        )
        
        nameLabel = DirectLabel(
            text=name,
            scale=0.032,
            pos=(-0.12, 0, 0),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ALeft,
            frameColor=(0, 0, 0, 0),
            parent=itemCard
        )
        
        # Hover effects
        itemCard.bind(DGG.ENTER, self.onItemHover, extraArgs=[itemCard])
        itemCard.bind(DGG.EXIT, self.onItemExit, extraArgs=[itemCard])

    def selectObjectItem(self, objectName):
        print(f"Selected object: {objectName}")
        for name, dot in self.satelliteDots.items():
            dot.setColor(1, 0, 0, 1) 
            dot.setScale(1.0) 
        
        if objectName in self.satelliteDots:
            self.satelliteDots[objectName].setColor(0, 1, 0, 1)  
            self.satelliteDots[objectName].setScale(2.0) 
        
        self.selectedSatellite = objectName
        
        if hasattr(self, 'detailsPanel'):
            self.detailsPanel.destroy()
            del self.detailsPanel
        
        self.createDetailsPanel(objectName)
        self.detailsPanelCreated = True
        
    def createDetailsPanel(self, objectName):
        self.detailsPanel = DirectFrame(
            frameColor=(0.02, 0.02, 0.08, 0.95),
            frameSize=(-0.35, 0.35, -0.45, 0.45),
            pos=(1.1, 0, 0.35),
            # relief=DGG.RAISED,
            borderWidth=(0.01, 0.01)
        )
        self.detailsPanel.setTransparency(TransparencyAttrib.MAlpha)
        
        closeBtn = DirectButton(
            image="../assets/close.png",
            scale=0.06,
            pos=(0.43, 0, 0.38),
            frameSize=(-0.8, 0.8, -0.6, 0.8),
            frameColor=(0.8, 0.2, 0.2, 0.9),
            # text_fg=(1, 1, 1, 1),
            command=self.closeDetailsPanel,
            parent=self.detailsPanel,
            relief=DGG.FLAT
        )
        
        
        titleLabel = DirectLabel(
            text="Satellite Details",
            scale=0.04,
            pos=(0, 0, 0.35),
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            parent=self.detailsPanel
        )
        
        nameLabel = DirectLabel(
            text=objectName,
            scale=0.045,
            pos=(0, 0, 0.25),
            text_fg=(0.3, 1, 0.3, 1),  
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            parent=self.detailsPanel
        )
        
        if objectName in self.satelliteTracker.satellites:
            lat, lon, alt = self.satelliteTracker.getPosition(objectName)
            
            latLabel = DirectLabel(
                text=f"Latitude: {lat:.4f}°",
                scale=0.035,
                pos=(0, 0, 0.12),
                text_fg=(0.9, 0.9, 0.9, 1),
                text_align=TextNode.ACenter,
                frameColor=(0, 0, 0, 0),
                parent=self.detailsPanel
            )
            
            lonLabel = DirectLabel(
                text=f"Longitude: {lon:.4f}°",
                scale=0.035,
                pos=(0, 0, 0.04),
                text_fg=(0.9, 0.9, 0.9, 1),
                text_align=TextNode.ACenter,
                frameColor=(0, 0, 0, 0),
                parent=self.detailsPanel
            )
            
            altLabel = DirectLabel(
                text=f"Altitude: {alt:.2f} km",
                scale=0.035,
                pos=(0, 0, -0.04),
                text_fg=(0.9, 0.9, 0.9, 1),
                text_align=TextNode.ACenter,
                frameColor=(0, 0, 0, 0),
                parent=self.detailsPanel
            )
            
            latHemi = "N" if lat >= 0 else "S"
            lonHemi = "E" if lon >= 0 else "W"
            
            hemisphereLabel = DirectLabel(
                text=f"Position: {abs(lat):.2f}°{latHemi}, {abs(lon):.2f}°{lonHemi}",
                scale=0.03,
                pos=(0, 0, -0.15),
                text_fg=(0.7, 0.7, 0.7, 1),
                text_align=TextNode.ACenter,
                frameColor=(0, 0, 0, 0),
                parent=self.detailsPanel
            )
            
            self.detailsLabels = {
                'lat': latLabel,
                'lon': lonLabel,
                'alt': altLabel,
                'hemisphere': hemisphereLabel,
                'name': objectName
            }
            
            if not hasattr(self, 'detailsUpdateTaskStarted'):
                self.taskMgr.add(self.updateDetailsTask, "updateDetails")
                self.detailsUpdateTaskStarted = True
                
    def updateDetailsTask(self, task):
        if not hasattr(self, 'detailsPanel') or not hasattr(self, 'detailsLabels'):
            return Task.cont
        
        objectName = self.detailsLabels['name']
        
        if objectName in self.satelliteTracker.satellites:
            lat, lon, alt = self.satelliteTracker.getPosition(objectName)
            
            self.detailsLabels['lat']['text'] = f"Latitude: {lat:.4f}°"
            self.detailsLabels['lon']['text'] = f"Longitude: {lon:.4f}°"
            self.detailsLabels['alt']['text'] = f"Altitude: {alt:.2f} km"
            
            latHemi = "N" if lat >= 0 else "S"
            lonHemi = "E" if lon >= 0 else "W"
            self.detailsLabels['hemisphere']['text'] = f"Position: {abs(lat):.2f}°{latHemi}, {abs(lon):.2f}°{lonHemi}"
        
        return Task.cont
    
    def closeDetailsPanel(self):
        if hasattr(self, 'detailsPanel'):
            self.detailsPanel.destroy()
            del self.detailsPanel
        
        if hasattr(self, 'detailsLabels'):
            del self.detailsLabels
        
        for name, dot in self.satelliteDots.items():
            dot.setColor(1, 0, 0, 1)
            dot.setScale(1.0)
        
    def onItemHover(self, itemCard, event):
        itemCard['frameColor'] = (0.25, 0.35, 0.45, 0.9)

    def onItemExit(self, itemCard, event):
        itemCard['frameColor'] = (0.18, 0.18, 0.18, 0.9)

    def nextPage(self):
        totalPages = (len(self.currentObjectList) + self.itemsPerPage - 1) // self.itemsPerPage
        if self.currentPage < totalPages - 1:
            self.currentPage += 1
            self.updateObjectList()

    def previousPage(self):
        if self.currentPage > 0:
            self.currentPage -= 1
            self.updateObjectList()
            
            
            
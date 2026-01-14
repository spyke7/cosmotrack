from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from panda3d.core import *
from direct.task import Task
import math
import random

class NaturalObject:
    def createEarth(self, render, loader):
        factor = 0.001
        
        equatorialRadius = 6378*factor
        polarRadius = 6357*factor
        
        self.loader = loader
        
        self.earth = self.createSphere()
        self.earth.reparentTo(render)
        self.earth.setPos(0,0,0)
        
        self.earth.setScale(equatorialRadius, equatorialRadius, polarRadius)

        self.earthTexture()
        
        return self.earth
    
    def createSphere(self, radius=1.0, segments=32):
        vformat = GeomVertexFormat.getV3n3t2()
        vdata = GeomVertexData("sphere", vformat, Geom.UHStatic)
        
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        texcoord = GeomVertexWriter(vdata, "texcoord")
        
        # vertices using lat and long
        for lat in range(segments + 1):
            theta = lat * math.pi / segments  
            sinTheta = math.sin(theta)
            cosTheta = math.cos(theta)
            
            v = lat/segments
            
            for lon in range(segments + 1):
                phi = lon * 2 * math.pi / segments 
                sinPhi = math.sin(phi)
                cosPhi = math.cos(phi)
                
                u = lon/segments
                
                x = cosPhi * sinTheta
                y = sinPhi * sinTheta
                z = cosTheta
                
                vertex.addData3(x * radius, y * radius, z * radius)
                normal.addData3(x, y, z)
                texcoord.addData2(u, v)
        
        geom = Geom(vdata)
        
        for lat in range(segments):
            for lon in range(segments):
                first = lat * (segments + 1) + lon
                second = first + segments + 1
                
                tri1 = GeomTriangles(Geom.UHStatic)
                tri1.addVertex(first)
                tri1.addVertex(second)
                tri1.addVertex(first + 1)
                tri1.closePrimitive()
                geom.addPrimitive(tri1)
                
                tri2 = GeomTriangles(Geom.UHStatic)
                tri2.addVertex(second)
                tri2.addVertex(second + 1)
                tri2.addVertex(first + 1)
                tri2.closePrimitive()
                geom.addPrimitive(tri2)
        
        node = GeomNode("sphere")
        node.addGeom(geom)
        return NodePath(node)
    
    def earthTexture(self):
        texture = self.loader.loadTexture("../assets/2k_earth_daymap.jpg")
        self.earth.setTexture(texture)
        self.earth.setTexRotate(TextureStage.getDefault(), 180)
        self.earth.setTexScale(TextureStage.getDefault(), -1, 1)
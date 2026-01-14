from panda3d.core import GeomNode, GeomVertexFormat, GeomVertexData, Geom, CardMaker
from panda3d.core import GeomTriangles, GeomVertexWriter, NodePath
import math

class ArtificialObject:
    
    def createSatelliteDot(self, radius=0.03, color=(1, 0, 0, 1)):
        dot = self.createSimpleSphere(radius=radius, segments=8)
        
        dot.setColor(color[0], color[1], color[2], color[3])
        
        return dot
    
    def createSimpleSphere(self, radius=1.0, segments=8):
        vformat = GeomVertexFormat.getV3n3()  # Only need vertex + normal, no texture
        vdata = GeomVertexData("sphere", vformat, Geom.UHStatic)
        
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        
        for lat in range(segments + 1):
            theta = lat * math.pi / segments  
            sinTheta = math.sin(theta)
            cosTheta = math.cos(theta)
            
            for lon in range(segments + 1):
                phi = lon * 2 * math.pi / segments 
                sinPhi = math.sin(phi)
                cosPhi = math.cos(phi)
                
                x = cosPhi * sinTheta
                y = sinPhi * sinTheta
                z = cosTheta
                
                vertex.addData3(x * radius, y * radius, z * radius)
                normal.addData3(x, y, z)
        
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
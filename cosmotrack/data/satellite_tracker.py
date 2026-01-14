from skyfield.api import load, EarthSatellite, wgs84
import math

class SatelliteTracker:
    def __init__(self):
        self.ts = load.timescale()
        
        self.satellites = {}
    
    def addSatellite(self, name, line1, line2):
        satellite = EarthSatellite(line1, line2, name, self.ts)
        self.satellites[name] = satellite
    
    def getPosition(self, satellite_name):
        if satellite_name not in self.satellites:
            return None
        
        t = self.ts.now()
        
        satellite = self.satellites[satellite_name]
        
        geocentric = satellite.at(t)
        
        # geographic coordinates (lat, lon, alt)
        subpoint = wgs84.subpoint(geocentric)
        
        lat = subpoint.latitude.degrees
        lon = subpoint.longitude.degrees
        alt = subpoint.elevation.km
        
        return (lat, lon, alt)
    
    def getAllPositions(self):
        positions = {}
        for name in self.satellites:
            pos = self.getPosition(name)
            if pos:
                positions[name] = pos
        return positions


def latLonAltTo3D(lat, lon, alt, earthRadius=6.378):
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    radius = earthRadius + (alt * 0.001)
    
    x = radius * math.cos(lat_rad) * math.cos(lon_rad)
    y = radius * math.cos(lat_rad) * math.sin(lon_rad)
    z = radius * math.sin(lat_rad)
    
    return (x, y, z)
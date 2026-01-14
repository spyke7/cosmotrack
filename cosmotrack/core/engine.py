from cosmotrack.data.tle_fetcher import getActiveSatellites, getSpaceStations
from cosmotrack.renderer.window import CosmotrackApp

def main():
    
    print("Fetching satellite data...")
    satelliteData = getActiveSatellites()
    satelliteDataLen = len(satelliteData)
    
    stationsData = getSpaceStations()
    stationsDataLen = len(stationsData)
    print(f"Fetched {satelliteDataLen} satellites and {stationsDataLen} space stations.")
    
    app = CosmotrackApp(satelliteData, stationsData)
    app.run() 
    
if __name__ == "__main__":
    main()
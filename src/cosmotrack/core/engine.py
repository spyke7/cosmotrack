from cosmotrack.data.tle_fetcher import getActiveSatellites, getSpaceStations
from cosmotrack.renderer.window import CosmotrackApp

def main():
    # names = getActiveSatellites()
    # print(len(names))
    # for name in names[:20]:
    #     print("-", name)
        
    
    # stations = getSpaceStations()
    # print(len(stations))
    # for station in stations[:20]:
    #     print("-", station)

    
    app = CosmotrackApp()
    app.run() 
    
if __name__ == "__main__":
    main()
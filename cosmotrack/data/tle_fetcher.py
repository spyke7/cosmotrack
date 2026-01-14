import requests

celestrak_url = ("https://celestrak.org/NORAD/elements/gp.php?", "GROUP=active&FORMAT=tle", "GROUP=stations&FORMAT=tle")

def getActiveSatellites():
    res = requests.get(celestrak_url[0]+celestrak_url[1], timeout=20)
    res.raise_for_status()
    
    lines = res.text.strip().splitlines()
    
    satellites = []
    for i in range(0, len(lines), 3):
        if (i+2 < len(lines)):
            name = lines[i].strip()
            name1 = lines[i+1].strip()
            name2 = lines[i+2].strip()
            satellites.append((name, name1, name2))
        
    return satellites

def getSpaceStations():
    res = requests.get(celestrak_url[0]+celestrak_url[2], timeout=20)
    res.raise_for_status()
    
    lines = res.text.strip().splitlines()
    
    stations = []
    for i in range(0, len(lines), 3):
        if (i+2 < len(lines)):
            name = lines[i].strip()
            name1 = lines[i+1].strip()
            name2 = lines[i+2].strip()
            stations.append((name, name1, name2))   

    return stations

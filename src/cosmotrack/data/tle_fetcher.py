import requests

celestrak_url = ("https://celestrak.org/NORAD/elements/gp.php?", "GROUP=active&FORMAT=tle", "GROUP=stations&FORMAT=tle")

def getActiveSatellites():
    res = requests.get(celestrak_url[0]+celestrak_url[1], timeout=20)
    res.raise_for_status()
    
    lines = res.text.strip().splitlines()
    
    names = []
    for i in range(0, len(lines), 3):
        names.append(lines[i].strip())
        
    return names

def getSpaceStations():
    res = requests.get(celestrak_url[0]+celestrak_url[2], timeout=20)
    res.raise_for_status()
    
    lines = res.text.strip().splitlines()
    
    names = []
    for i in range(0, len(lines), 3):
        names.append(lines[i].strip())
        
    return names
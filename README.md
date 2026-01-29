# Cosmotrack

A 3D visualization tool to track satellites, stations and more revolving around Earth.

### Features
- [x] 3D earth rendered, can be rotated with mouse, and rotates around its own axis according to the real time.
- [x] Satellite and stations live movement around Earth
- [x] Details Panel showed for selected objects
- [ ] Adding Sun, and moon, so that Earth can be revolved around the Sun, and adding more physics on it.....

### Getting started
- Download the requirements - 
`pip install -r requirements.txt`

- Run the engine
`py -m cosmotrack.core.engine`

### Documentation
Cosmostrack is made using panda3D graphics library and skyfield.
The `tle` data is taken from [celestrak - NORAD](https://celestrak.org/NORAD/elements/), thanks to their free api.
For the satellites - [satellite data](https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle)
For the space stations - [stations data](https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle)

##### Data extraction and satellite tracking
The data is fetched inside `data\tle_fetcher.py`. The number of active or the satellites is huge (approx 14K to 15K). That is why we render only about 30. And the number of stations is relatively very small, so we render all of them.

Inside `data\satellite_tracker.py`, we use skyfield. In the `getPosition()` function, we get lat, lon, alt from the tle data, by passing the data to the `EarthSatellite` class of skyfield and getting subpoint using the `wgs84`.
The x,y,z components are also calculated here. (More on that inside the render part)

##### Rendering 
*renderer foler*
The main file that renders the window is `window.py`
- `setup3DScene` is setting up the lighting, rotating the mouse, rotating the earth, and has the main sceneRoot. The rotation of earth is kept as real as possible. (HPR - Head, Pitch, Roll)
- `sideBarHandler` is the left navbar, and where all the other things are made. Also you can see that most of the things whether it is the navbar, or a dropdown, is a DirectFrame. 
- `selectArtificialObject` - Gives options - Satellites, Stations, None. For selecting Satellites and Stations, it calls the `updateObjectList` and `initializeSatellites` functions. 
    - `initializeSatellites` function, generates a small circle for each element in the Satellite list, and also adds them to the object made for the `satellite_tracker.py`.
    - `updateSatellitesTask` is to update the positions continuously with the help of `latLonAltTo3D` function of `satellite_tracker.py`
    - The selected satellite/station from the dropdown will be highlighted as green and rest as red.
- There is a right details panel as well, which shows lat, lon, alt and hemisphere details.

The `naturalobjects.py` is for creating Earth as a smooth sphere.
The `createSphere` is used for creating smooth sphere with desired radius and segments. The more the number of segments the smoother the sphere.
- vertex, normal, texcoord is used for drawing vertices, normals and texture. `vformat = GeomVertexFormat.getV3n3t2()` gives V3->3D positions, n3 -> 3D normal vectors, t2 -> texture (u,v -> horizontal,vertical (btw 0 and 1))
- The latitude varies from 0 deg to 180 deg (N to S) represented by theta. The longitude varies from 0 deg to 360 deg, represented with phi. So the cartesian coordinates are represented as - 
    - x = r * cos(phi) * sin(theta)
    - y = r * sin(phi) * sin(theta)
    - z = r * cos(theta)
    This is done in the first nested loop.

    - In the second loop, triangles are drawn accordingly. As squares cannot be draw, i.e, why two triangles are drawn.

In the same way, the small circles are created in `artificialobjects.py`

The main loop is inside the `core\engine.py`.

### Screenshots
<img width="1489" height="945" alt="details1" src="https://github.com/user-attachments/assets/9c10e9dc-06ae-468f-8d6f-80abd40a4ce0" />


### Contributing and Support
If you liked it, please give a star to my project.
All contributors are welcomed. You can raise issues or directly raise a PR (if possible describe the features/bug).
I would definitely appreciate if you can integrate new features or future features.

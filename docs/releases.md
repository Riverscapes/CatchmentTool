---
title: Releases
---

* [Catchment Tool version 1.4](https://github.com/Riverscapes/CatchmentTool/archive/master.zip)
  * Download and unzip the file into a directory, then add the **Catchment Tool** toolbox into ArcGIS using `ArcToolbox > Add Toolbox`.

### Updates and Release Notes
2/2/2018
* Fixed issue with grid code field name, when delineating RCAs.

10/26/2017
* Added Repair Geometry to processing.

10/25/2017
* New version uploaded, v1.2.
* Fixed small error due to incorrect value in polygon thickness calculation.

10/24/2017
* New version uploaded, v1.1. 
* Added additional error check based on calculated "thinness" of each catchment area polygon.

8/6/2017
* Transferred repository from [SouthForkResearch](https://github.com/SouthForkResearch) to [Riverscapes](https://github.com/Riverscapes)

11/9/2016
* Transferred repository from [jesselangdon](https://github.com/jesselangdon) to [SouthForkResearch](https://github.com/SouthForkResearch) 

10/05/2016
* Changed name from RCA Tools to Catchment Tool, uploaded v1.0
* The *Segment Stream Network* tool has been removed and incorporated into GNAT.

9/8/2016
* New version uploaded, v0.5
* Changes and revisions:
  * Added data pre-processing steps to the Segment Stream Network tool
  	* includes calculating stream order and branch IDs, using GNAT modules.
  * Added new module to more thoroughly clean up in_memory data sets.

8/8/2016
* New version uploaded, v0.4
* Changes and revisions include:
  * moved endpoint generation to Delineate Catchments tool. 
  * revised related inputs and outputs in tool interfaces.
  * improved alignment of catchment area polygons with stream segments.

8/3/2016
* New version uploaded, v0.3
* Changes and revisions include:
  * improved segmentation algorithm
  * added metadata output
  * minor interface improvements

7/28/2016
* Release RCA Tools, v0.1
  * Initial public release